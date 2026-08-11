from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APITestCase

from authentication.models import Customer, Organizer, User
from events.models import Event, EventStatusEnum, TicketType
from orders.models import OrderStatusEnum
from orders.services import hold_seats
from seating.models import Seat, SeatStatusEnum


class SeatApiTests(APITestCase):
    def setUp(self):
        organizer_user = User.objects.create_user(
            username='seat-organizer',
            email='seat-organizer@example.com',
            phone_number='0904000001',
            name='Seat Organizer',
            type='ORGANIZER',
            password='123456',
        )
        self.organizer = Organizer.objects.create(
            user=organizer_user,
            company_name='Seat Company',
            bank_account='123456789',
        )
        customer_user = User.objects.create_user(
            username='seat-customer',
            email='seat-customer@example.com',
            phone_number='0904000002',
            name='Seat Customer',
            type='CUSTOMER',
            password='123456',
        )
        self.customer = Customer.objects.create(user=customer_user)
        self.admin_user = User.objects.create_superuser(
            username='seat-admin',
            email='seat-admin@example.com',
            phone_number='0904000003',
            name='Seat Admin',
            password='123456',
        )
        self.event = Event.objects.create(
            organizer=self.organizer,
            title='Seat Event',
            thumbnail='https://example.com/event.jpg',
            description='Seat test event',
            location='TP.HCM',
            start_time=timezone.now() + timedelta(days=1),
            status=EventStatusEnum.PUBLISHED,
        )
        self.ticket_type = TicketType.objects.create(
            event=self.event,
            name='VIP',
            price=150000,
            quantity=3,
        )
        self.seats = [
            Seat.objects.create(
                event=self.event,
                ticket_type=self.ticket_type,
                row=row,
                number=number,
            )
            for row, number in [('B', 2), ('A', 2), ('A', 1)]
        ]

    def make_order_expired(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        past = timezone.now() - timedelta(seconds=1)
        order.expires_at = past
        order.save(update_fields=['expires_at'])
        Seat.objects.filter(id=self.seats[0].id).update(locked_until=past)
        return order

    def test_published_event_returns_ordered_seat_map(self):
        response = self.client.get(f'/api/seats/event/{self.event.id}/')

        seat_names = [seat['seat_name'] for seat in response.data]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(seat_names, ['A-1', 'A-2', 'B-2'])
        self.assertEqual(response.data[0]['status'], SeatStatusEnum.AVAILABLE)
        self.assertEqual(response.data[0]['ticket_type_name'], 'VIP')
        self.assertEqual(response.data[0]['price'], '150000.00')

    def test_pending_and_cancelled_event_seat_maps_are_hidden(self):
        self.event.status = EventStatusEnum.PENDING
        self.event.save(update_fields=['status'])
        pending_response = self.client.get(
            f'/api/seats/event/{self.event.id}/'
        )

        self.event.status = EventStatusEnum.CANCELLED
        self.event.save(update_fields=['status'])
        cancelled_response = self.client.get(
            f'/api/seats/event/{self.event.id}/'
        )

        self.assertEqual(pending_response.status_code, 404)
        self.assertEqual(cancelled_response.status_code, 404)

    def test_loading_seat_map_releases_expired_order(self):
        order = self.make_order_expired()

        # Act: tải lại sơ đồ ghế cũng kích hoạt xử lý đơn hết hạn.
        response = self.client.get(f'/api/seats/event/{self.event.id}/')

        order.refresh_from_db()
        self.seats[0].refresh_from_db()
        returned_seat = next(
            seat for seat in response.data if seat['id'] == self.seats[0].id
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(order.status, OrderStatusEnum.EXPIRED)
        self.assertEqual(self.seats[0].status, SeatStatusEnum.AVAILABLE)
        self.assertEqual(returned_seat['status'], SeatStatusEnum.AVAILABLE)

    def test_only_admin_can_release_expired_orders_manually(self):
        order = self.make_order_expired()

        anonymous_response = self.client.post('/api/seats/release-expired/')
        self.client.force_authenticate(self.customer.user)
        customer_response = self.client.post('/api/seats/release-expired/')
        self.client.force_authenticate(self.admin_user)
        admin_response = self.client.post('/api/seats/release-expired/')

        order.refresh_from_db()
        self.seats[0].refresh_from_db()
        self.assertEqual(anonymous_response.status_code, 401)
        self.assertEqual(customer_response.status_code, 403)
        self.assertEqual(admin_response.status_code, 200)
        self.assertEqual(admin_response.data['expired_orders'], 1)
        self.assertEqual(order.status, OrderStatusEnum.EXPIRED)
        self.assertEqual(self.seats[0].status, SeatStatusEnum.AVAILABLE)
