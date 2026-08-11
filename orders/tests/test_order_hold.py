from datetime import timedelta

from django.utils import timezone

from events.models import EventStatusEnum
from orders.models import OrderStatusEnum, Ticket
from orders.services import (
    OrderLifecycleError,
    cancel_pending_order,
    expire_stale_orders,
    hold_seats,
)
from seating.models import Seat, SeatStatusEnum

from .base import OrderTestBase


class OrderHoldTests(OrderTestBase):
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

    def test_hold_creates_order_items_without_issuing_tickets(self):
        # Act: giữ hai ghế còn trống.
        order = hold_seats(
            self.customer,
            [self.seats[0].id, self.seats[1].id],
        )

        # Assert: đơn PENDING được tạo, ghế khóa 10 phút và chưa phát hành vé.
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
            hold_seats(
                self.customer,
                [self.seats[0].id, self.other_seat.id],
            )

        self.assertEqual(context.exception.code, 'mixed_events')

    def test_rejects_more_than_five_seats(self):
        with self.assertRaises(OrderLifecycleError) as context:
            hold_seats(self.customer, [seat.id for seat in self.seats])

        self.assertEqual(context.exception.code, 'seat_limit_exceeded')

    def test_second_customer_cannot_hold_a_locked_seat(self):
        hold_seats(self.customer, [self.seats[0].id])
        other_customer = self.create_customer(5)

        with self.assertRaises(OrderLifecycleError) as context:
            hold_seats(other_customer, [self.seats[0].id])

        self.assertEqual(context.exception.code, 'seat_locked')

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
