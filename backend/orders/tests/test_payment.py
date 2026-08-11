from datetime import timedelta

from django.utils import timezone

from orders.models import OrderStatusEnum, Payment, Ticket
from orders.services import (
    OrderLifecycleError,
    cancel_pending_order,
    confirm_order_payment,
    expire_stale_orders,
    hold_seats,
)
from seating.models import Seat, SeatStatusEnum

from .base import OrderTestBase


class PaymentServiceTests(OrderTestBase):
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

        other_customer = self.create_customer(2)
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
        order = hold_seats(
            self.customer,
            [self.seats[0].id, self.seats[1].id],
        )

        # Act: xác nhận cùng một giao dịch hai lần.
        paid_order, processed = confirm_order_payment(
            order.id,
            amount=200000,
            transaction_id='PAYOS-001',
        )
        _, processed_again = confirm_order_payment(
            order.id,
            amount=200000,
            transaction_id='PAYOS-001',
        )

        # Assert: trạng thái cuối chỉ có một Payment và một vé cho mỗi ghế.
        self.assertTrue(processed)
        self.assertFalse(processed_again)
        self.assertEqual(paid_order.status, OrderStatusEnum.PAID)
        self.assertEqual(Ticket.objects.filter(order=paid_order).count(), 2)
        self.assertEqual(Payment.objects.filter(order=paid_order).count(), 1)
        for seat in self.seats[:2]:
            seat.refresh_from_db()
            self.assertEqual(seat.status, SeatStatusEnum.SOLD)
            self.assertIsNone(seat.locked_by_order_id)

    def test_cancelled_order_cannot_be_paid(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        cancel_pending_order(order.id, customer=self.customer)

        with self.assertRaises(OrderLifecycleError) as context:
            confirm_order_payment(
                order.id,
                amount=100000,
                transaction_id='PAYOS-002',
            )

        self.assertEqual(context.exception.code, 'invalid_payment_state')

    def test_amount_mismatch_does_not_sell_seat(self):
        order = hold_seats(self.customer, [self.seats[0].id])

        with self.assertRaises(OrderLifecycleError) as context:
            confirm_order_payment(
                order.id,
                amount=99999,
                transaction_id='PAYOS-003',
            )

        order.refresh_from_db()
        self.seats[0].refresh_from_db()
        self.assertEqual(context.exception.code, 'amount_mismatch')
        self.assertEqual(order.status, OrderStatusEnum.PENDING)
        self.assertEqual(self.seats[0].status, SeatStatusEnum.LOCKED)
        self.assertEqual(Ticket.objects.count(), 0)
