from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier

from django.db import close_old_connections
from django.test import TransactionTestCase
from django.utils import timezone

from authentication.models import Customer, Organizer, User
from events.models import Event, EventStatusEnum, TicketType
from orders.models import Order, OrderItem
from orders.services import OrderLifecycleError, hold_seats
from seating.models import Seat, SeatStatusEnum


class SeatRaceConditionTests(TransactionTestCase):
    def setUp(self):
        organizer_user = User.objects.create_user(
            username='race-organizer',
            email='race-organizer@example.com',
            phone_number='0904000011',
            name='Race Organizer',
            type='ORGANIZER',
            password='123456',
        )
        organizer = Organizer.objects.create(
            user=organizer_user,
            company_name='Race Company',
            bank_account='123456789',
        )
        self.customer_ids = []
        for number in (1, 2):
            user = User.objects.create_user(
                username=f'race-customer-{number}',
                email=f'race-customer-{number}@example.com',
                phone_number=f'090400001{number + 1}',
                name=f'Race Customer {number}',
                type='CUSTOMER',
                password='123456',
            )
            customer = Customer.objects.create(user=user)
            self.customer_ids.append(customer.pk)

        event = Event.objects.create(
            organizer=organizer,
            title='Race Event',
            thumbnail='https://example.com/event.jpg',
            description='Race condition test',
            location='TP.HCM',
            start_time=timezone.now() + timedelta(days=1),
            status=EventStatusEnum.PUBLISHED,
        )
        ticket_type = TicketType.objects.create(
            event=event,
            name='VIP',
            price=100000,
            quantity=1,
        )
        self.seat = Seat.objects.create(
            event=event,
            ticket_type=ticket_type,
            row='A',
            number=1,
        )

    def try_to_hold_same_seat(self, customer_id, barrier):
        # Mỗi thread dùng kết nối database riêng như hai request thật.
        close_old_connections()
        try:
            customer = Customer.objects.get(pk=customer_id)
            barrier.wait(timeout=5)
            order = hold_seats(customer, [self.seat.id])
            return 'success', order.id
        except OrderLifecycleError as error:
            return error.code, None
        finally:
            close_old_connections()

    def test_only_one_customer_can_hold_the_same_seat(self):
        # Arrange: đồng bộ để hai luồng bắt đầu giữ cùng một ghế gần như cùng lúc.
        barrier = Barrier(2)

        # Act: chạy hai yêu cầu song song.
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(
                    self.try_to_hold_same_seat,
                    customer_id,
                    barrier,
                )
                for customer_id in self.customer_ids
            ]
            results = [future.result(timeout=15) for future in futures]

        # Assert: đúng một đơn thắng, đơn còn lại nhận lỗi seat_locked.
        result_codes = sorted(result[0] for result in results)
        self.assertEqual(result_codes, ['seat_locked', 'success'])
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        self.seat.refresh_from_db()
        self.assertEqual(self.seat.status, SeatStatusEnum.LOCKED)
        self.assertEqual(self.seat.locked_by_order_id, Order.objects.get().id)
