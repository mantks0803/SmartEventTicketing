from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from authentication.models import Customer, Organizer, User
from events.models import Event, TicketType
from orders.models import OrderStatusEnum, Payment, Ticket
from orders.services import (
    OrderLifecycleError,
    cancel_pending_order,
    confirm_order_payment,
    expire_stale_orders,
    hold_seats,
)
from seating.models import Seat, SeatStatusEnum


class OrderLifecycleTests(TestCase):
    def setUp(self):
        customer_user = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            phone_number='0900000001',
            name='Customer',
            type='CUSTOMER',
            password='123456',
        )
        self.customer = Customer.objects.create(user=customer_user)

        self.organizer_user = User.objects.create_user(
            username='organizer',
            email='organizer@example.com',
            phone_number='0900000002',
            name='Organizer',
            type='ORGANIZER',
            password='123456',
        )
        self.organizer = Organizer.objects.create(
            user=self.organizer_user,
            company_name='SmartTicket',
            bank_account='123456',
        )

        self.event = self._create_event('Event 1')
        self.other_event = self._create_event('Event 2')
        self.ticket_type = TicketType.objects.create(
            event=self.event,
            name='VIP',
            price=100000,
            quantity=10,
        )
        self.other_ticket_type = TicketType.objects.create(
            event=self.other_event,
            name='VIP',
            price=200000,
            quantity=10,
        )
        self.seats = [
            Seat.objects.create(
                event=self.event,
                ticket_type=self.ticket_type,
                row='A',
                number=number,
            )
            for number in range(1, 7)
        ]
        self.other_seat = Seat.objects.create(
            event=self.other_event,
            ticket_type=self.other_ticket_type,
            row='B',
            number=1,
        )

    def _create_event(self, title):
        return Event.objects.create(
            organizer=self.organizer,
            title=title,
            thumbnail='https://example.com/event.jpg',
            description='Test event',
            location='TP.HCM',
            start_time=timezone.now() + timedelta(days=1),
        )

    def test_hold_creates_order_items_without_issuing_tickets(self):
        order = hold_seats(self.customer, [self.seats[0].id, self.seats[1].id])

        self.assertEqual(order.status, OrderStatusEnum.PENDING)
        self.assertEqual(order.items.count(), 2)
        self.assertEqual(order.tickets.count(), 0)

        for seat in self.seats[:2]:
            seat.refresh_from_db()
            self.assertEqual(seat.status, SeatStatusEnum.LOCKED)
            self.assertEqual(seat.locked_by_order_id, order.id)
            self.assertEqual(seat.locked_until, order.expires_at)

    def test_rejects_seats_from_different_events(self):
        with self.assertRaises(OrderLifecycleError) as context:
            hold_seats(self.customer, [self.seats[0].id, self.other_seat.id])

        self.assertEqual(context.exception.code, 'mixed_events')

    def test_rejects_more_than_five_seats(self):
        with self.assertRaises(OrderLifecycleError) as context:
            hold_seats(self.customer, [seat.id for seat in self.seats])

        self.assertEqual(context.exception.code, 'seat_limit_exceeded')

    def test_cancelled_seat_can_be_held_again(self):
        first_order = hold_seats(self.customer, [self.seats[0].id])
        cancel_pending_order(first_order.id, customer=self.customer)

        self.seats[0].refresh_from_db()
        self.assertEqual(self.seats[0].status, SeatStatusEnum.AVAILABLE)
        self.assertIsNone(self.seats[0].locked_by_order_id)
        self.assertEqual(Ticket.objects.count(), 0)

        second_order = hold_seats(self.customer, [self.seats[0].id])
        self.assertNotEqual(first_order.id, second_order.id)
        self.assertEqual(second_order.items.count(), 1)

    def test_expired_order_releases_its_seats(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        past = timezone.now() - timedelta(seconds=1)
        order.expires_at = past
        order.save(update_fields=['expires_at'])
        Seat.objects.filter(id=self.seats[0].id).update(locked_until=past)

        expired_count = expire_stale_orders()

        order.refresh_from_db()
        self.seats[0].refresh_from_db()
        self.assertEqual(expired_count, 1)
        self.assertEqual(order.status, OrderStatusEnum.EXPIRED)
        self.assertEqual(self.seats[0].status, SeatStatusEnum.AVAILABLE)
        self.assertIsNone(self.seats[0].locked_by_order_id)

    def test_successful_payment_sells_seats_and_issues_tickets_once(self):
        order = hold_seats(self.customer, [self.seats[0].id, self.seats[1].id])

        paid_order, processed = confirm_order_payment(
            order.id,
            amount=200000,
            transaction_id='PAYOS-001',
        )

        self.assertTrue(processed)
        self.assertEqual(paid_order.status, OrderStatusEnum.PAID)
        self.assertEqual(Ticket.objects.filter(order=paid_order).count(), 2)
        self.assertEqual(Payment.objects.filter(order=paid_order).count(), 1)

        for seat in self.seats[:2]:
            seat.refresh_from_db()
            self.assertEqual(seat.status, SeatStatusEnum.SOLD)
            self.assertIsNone(seat.locked_by_order_id)

        _, processed_again = confirm_order_payment(
            order.id,
            amount=200000,
            transaction_id='PAYOS-001',
        )
        self.assertFalse(processed_again)
        self.assertEqual(Ticket.objects.filter(order=paid_order).count(), 2)
        self.assertEqual(Payment.objects.filter(order=paid_order).count(), 1)

    def test_cancelled_order_cannot_be_paid(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        cancel_pending_order(order.id, customer=self.customer)

        with self.assertRaises(OrderLifecycleError) as context:
            confirm_order_payment(order.id, amount=100000, transaction_id='PAYOS-002')

        self.assertEqual(context.exception.code, 'invalid_payment_state')

    def test_amount_mismatch_does_not_sell_seat(self):
        order = hold_seats(self.customer, [self.seats[0].id])

        with self.assertRaises(OrderLifecycleError) as context:
            confirm_order_payment(order.id, amount=99999, transaction_id='PAYOS-003')

        self.assertEqual(context.exception.code, 'amount_mismatch')
        order.refresh_from_db()
        self.seats[0].refresh_from_db()
        self.assertEqual(order.status, OrderStatusEnum.PENDING)
        self.assertEqual(self.seats[0].status, SeatStatusEnum.LOCKED)
        self.assertEqual(Ticket.objects.count(), 0)

    def test_webhook_is_idempotent(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        payload = {
            'success': True,
            'code': '00',
            'data': {
                'orderCode': order.id,
                'amount': 100000,
                'reference': 'PAYOS-WEBHOOK-001',
            },
        }
        client = APIClient()

        first_response = client.post('/api/orders/webhook/payos/', payload, format='json')
        second_response = client.post('/api/orders/webhook/payos/', payload, format='json')

        order.refresh_from_db()
        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(first_response.data['status'], 'success')
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(second_response.data['status'], 'already_processed')
        self.assertEqual(order.status, OrderStatusEnum.PAID)
        self.assertEqual(order.tickets.count(), 1)
        self.assertEqual(order.payments.count(), 1)

    def test_success_webhook_cannot_revive_cancelled_order(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        cancel_pending_order(order.id, customer=self.customer)
        client = APIClient()

        response = client.post(
            '/api/orders/webhook/payos/',
            {
                'success': True,
                'code': '00',
                'data': {
                    'orderCode': order.id,
                    'amount': 100000,
                    'reference': 'PAYOS-WEBHOOK-002',
                },
            },
            format='json',
        )

        order.refresh_from_db()
        self.seats[0].refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ignored')
        self.assertEqual(order.status, OrderStatusEnum.CANCELLED)
        self.assertEqual(self.seats[0].status, SeatStatusEnum.AVAILABLE)
        self.assertEqual(order.tickets.count(), 0)

    def test_pending_ticket_cannot_be_checked_in(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        ticket = Ticket.objects.create(
            order=order,
            seat=self.seats[0],
            ticket_type=self.ticket_type,
            qr_code='LEGACY-PENDING-TICKET',
        )
        client = APIClient()
        client.force_authenticate(self.organizer_user)

        response = client.post(
            '/api/orders/check-in/',
            {'qr_code': ticket.qr_code},
            format='json',
        )

        ticket.refresh_from_db()
        self.assertEqual(response.status_code, 400)
        self.assertFalse(ticket.is_checked_in)
