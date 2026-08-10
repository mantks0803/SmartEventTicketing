from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from authentication.models import Customer, Organizer, User
from events.models import Event, EventStatusEnum, TicketType
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
            status=EventStatusEnum.PUBLISHED,
        )

    def test_pending_event_cannot_be_held(self):
        self.event.status = EventStatusEnum.PENDING
        self.event.save(update_fields=['status'])

        with self.assertRaises(OrderLifecycleError) as context:
            hold_seats(self.customer, [self.seats[0].id])

        self.assertEqual(context.exception.code, 'event_not_published')

    def test_started_event_cannot_be_held(self):
        self.event.start_time = timezone.now() - timedelta(minutes=1)
        self.event.save(update_fields=['start_time'])

        with self.assertRaises(OrderLifecycleError) as context:
            hold_seats(self.customer, [self.seats[0].id])

        self.assertEqual(context.exception.code, 'event_already_started')

    def test_payos_link_is_blocked_after_event_is_cancelled(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        self.event.status = EventStatusEnum.CANCELLED
        self.event.save(update_fields=['status'])

        client = APIClient()
        client.force_authenticate(self.customer.user)
        response = client.post(
            f'/api/orders/{order.id}/payos-link/',
            {},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 'event_not_published')

    def test_payos_link_is_blocked_after_event_has_started(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        self.event.start_time = timezone.now() - timedelta(minutes=1)
        self.event.save(update_fields=['start_time'])

        client = APIClient()
        client.force_authenticate(self.customer.user)
        response = client.post(
            f'/api/orders/{order.id}/payos-link/',
            {},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 'event_already_started')

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

    def test_verified_payment_can_restore_expired_order_when_seat_is_available(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        past = timezone.now() - timedelta(seconds=1)
        order.expires_at = past
        order.save(update_fields=['expires_at'])
        Seat.objects.filter(id=self.seats[0].id).update(locked_until=past)
        expire_stale_orders()

        paid_order, processed = confirm_order_payment(
            order.id,
            amount=100000,
            transaction_id='PAYOS-LATE-001',
            allow_expired=True,
        )

        paid_order.refresh_from_db()
        self.seats[0].refresh_from_db()
        self.assertTrue(processed)
        self.assertEqual(paid_order.status, OrderStatusEnum.PAID)
        self.assertEqual(self.seats[0].status, SeatStatusEnum.SOLD)
        self.assertEqual(paid_order.tickets.count(), 1)
        self.assertEqual(paid_order.payments.count(), 1)

    def test_verified_late_payment_does_not_take_seat_from_another_order(self):
        old_order = hold_seats(self.customer, [self.seats[0].id])
        past = timezone.now() - timedelta(seconds=1)
        old_order.expires_at = past
        old_order.save(update_fields=['expires_at'])
        Seat.objects.filter(id=self.seats[0].id).update(locked_until=past)
        expire_stale_orders()

        other_user = User.objects.create_user(
            username='other-customer',
            email='other@example.com',
            phone_number='0900000003',
            name='Other Customer',
            type='CUSTOMER',
            password='123456',
        )
        other_customer = Customer.objects.create(user=other_user)
        new_order = hold_seats(other_customer, [self.seats[0].id])

        with self.assertRaises(OrderLifecycleError) as context:
            confirm_order_payment(
                old_order.id,
                amount=100000,
                transaction_id='PAYOS-LATE-002',
                allow_expired=True,
            )

        old_order.refresh_from_db()
        self.seats[0].refresh_from_db()
        self.assertEqual(context.exception.code, 'seat_unavailable_after_payment')
        self.assertEqual(old_order.status, OrderStatusEnum.EXPIRED)
        self.assertEqual(self.seats[0].status, SeatStatusEnum.LOCKED)
        self.assertEqual(self.seats[0].locked_by_order_id, new_order.id)
        self.assertEqual(old_order.tickets.count(), 0)

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

    @override_settings(
        PAYOS_SKIP_SIGNATURE_CHECK=True,
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='SmartTicket <noreply@smartticket.test>',
    )
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

        with self.captureOnCommitCallbacks(execute=True):
            first_response = client.post(
                '/api/orders/webhook/payos/',
                payload,
                format='json',
            )

        with self.captureOnCommitCallbacks(execute=True):
            second_response = client.post(
                '/api/orders/webhook/payos/',
                payload,
                format='json',
            )

        order.refresh_from_db()
        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(first_response.data['status'], 'success')
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(second_response.data['status'], 'already_processed')
        self.assertEqual(order.status, OrderStatusEnum.PAID)
        self.assertEqual(order.tickets.count(), 1)
        self.assertEqual(order.payments.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['customer@example.com'])
        self.assertIn(f'#{order.id}', mail.outbox[0].subject)

    @override_settings(PAYOS_SKIP_SIGNATURE_CHECK=True)
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

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='SmartTicket <noreply@smartticket.test>',
    )
    def test_customer_can_reconcile_paid_order_directly_with_payos(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        payment_info = SimpleNamespace(
            status='PAID',
            orderCode=order.id,
            amount=100000,
            amountPaid=100000,
            amountRemaining=0,
            id='payment-link-001',
            transactions=[SimpleNamespace(reference='PAYOS-RECONCILE-001')],
        )
        client = APIClient()
        client.force_authenticate(self.customer.user)

        with patch('orders.views.payos') as payos_mock:
            payos_mock.getPaymentLinkInformation.return_value = payment_info
            with self.captureOnCommitCallbacks(execute=True):
                response = client.post(
                    f'/api/orders/{order.id}/reconcile-payos/',
                    {},
                    format='json',
                )
                second_response = client.post(
                    f'/api/orders/{order.id}/reconcile-payos/',
                    {},
                    format='json',
                )

        order.refresh_from_db()
        self.seats[0].refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['payos_status'], 'PAID')
        self.assertEqual(response.data['order']['status'], OrderStatusEnum.PAID)
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(second_response.data['status'], 'success')
        self.assertEqual(order.status, OrderStatusEnum.PAID)
        self.assertEqual(self.seats[0].status, SeatStatusEnum.SOLD)
        self.assertEqual(order.tickets.count(), 1)
        self.assertEqual(order.payments.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_pending_payos_reconciliation_does_not_issue_ticket(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        payment_info = SimpleNamespace(status='PENDING')
        client = APIClient()
        client.force_authenticate(self.customer.user)

        with patch('orders.views.payos') as payos_mock:
            payos_mock.getPaymentLinkInformation.return_value = payment_info
            response = client.post(
                f'/api/orders/{order.id}/reconcile-payos/',
                {},
                format='json',
            )

        order.refresh_from_db()
        self.seats[0].refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'waiting')
        self.assertEqual(response.data['payos_status'], 'PENDING')
        self.assertEqual(order.status, OrderStatusEnum.PENDING)
        self.assertEqual(self.seats[0].status, SeatStatusEnum.LOCKED)
        self.assertEqual(order.tickets.count(), 0)
        self.assertEqual(order.payments.count(), 0)

    def test_reconciliation_rejects_mismatched_payos_order_data(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        payment_info = SimpleNamespace(
            status='PAID',
            orderCode=order.id + 999,
            amount=100000,
            amountPaid=100000,
            amountRemaining=0,
            transactions=[SimpleNamespace(reference='PAYOS-WRONG-ORDER')],
        )
        client = APIClient()
        client.force_authenticate(self.customer.user)

        with patch('orders.views.payos') as payos_mock:
            payos_mock.getPaymentLinkInformation.return_value = payment_info
            response = client.post(
                f'/api/orders/{order.id}/reconcile-payos/',
                {},
                format='json',
            )

        order.refresh_from_db()
        self.seats[0].refresh_from_db()
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data['code'], 'payos_data_mismatch')
        self.assertEqual(order.status, OrderStatusEnum.PENDING)
        self.assertEqual(self.seats[0].status, SeatStatusEnum.LOCKED)
        self.assertEqual(order.tickets.count(), 0)
        self.assertEqual(order.payments.count(), 0)

    def test_customer_cannot_reconcile_another_customers_order(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        other_user = User.objects.create_user(
            username='idor-customer',
            email='idor@example.com',
            phone_number='0900000004',
            name='IDOR Customer',
            type='CUSTOMER',
            password='123456',
        )
        Customer.objects.create(user=other_user)
        client = APIClient()
        client.force_authenticate(other_user)

        with patch('orders.views.payos') as payos_mock:
            response = client.post(
                f'/api/orders/{order.id}/reconcile-payos/',
                {},
                format='json',
            )

        order.refresh_from_db()
        self.assertEqual(response.status_code, 404)
        payos_mock.getPaymentLinkInformation.assert_not_called()
        self.assertEqual(order.status, OrderStatusEnum.PENDING)
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
