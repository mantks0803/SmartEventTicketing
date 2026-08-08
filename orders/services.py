import uuid
from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from orders.models import (
    Order,
    OrderItem,
    OrderStatusEnum,
    Payment,
    PaymentStatusEnum,
    Ticket,
)
from seating.models import Seat, SeatStatusEnum


MAX_SEATS_PER_ORDER = 5
SEAT_HOLD_MINUTES = 10


class OrderLifecycleError(Exception):
    def __init__(self, message, code='invalid_order_state'):
        super().__init__(message)
        self.message = message
        self.code = code


def _release_locked_seats(order):
    return Seat.objects.filter(
        locked_by_order=order,
        status=SeatStatusEnum.LOCKED,
    ).update(
        status=SeatStatusEnum.AVAILABLE,
        locked_until=None,
        locked_by_order=None,
    )


@transaction.atomic
def expire_order(order_id, now=None):
    now = now or timezone.now()
    order = Order.objects.select_for_update().get(id=order_id)

    if order.status != OrderStatusEnum.PENDING:
        return False

    if not order.expires_at or order.expires_at > now:
        return False

    _release_locked_seats(order)
    order.status = OrderStatusEnum.EXPIRED
    order.payos_checkout_url = None
    order.save(update_fields=['status', 'payos_checkout_url', 'updated_at'])
    return True


def expire_stale_orders(now=None):
    now = now or timezone.now()
    order_ids = list(
        Order.objects.filter(
            status=OrderStatusEnum.PENDING,
            expires_at__isnull=False,
            expires_at__lte=now,
        ).values_list('id', flat=True)
    )

    expired_count = 0
    for order_id in order_ids:
        if expire_order(order_id, now=now):
            expired_count += 1

    return expired_count


def hold_seats(customer, seat_ids):
    unique_seat_ids = list(dict.fromkeys(seat_ids))

    if len(unique_seat_ids) != len(seat_ids):
        raise OrderLifecycleError('Danh sách ghế không được chứa ID trùng lặp.', 'duplicate_seats')

    if not unique_seat_ids:
        raise OrderLifecycleError('Vui lòng chọn ít nhất một ghế.', 'empty_seats')

    if len(unique_seat_ids) > MAX_SEATS_PER_ORDER:
        raise OrderLifecycleError(
            f'Mỗi đơn hàng chỉ được chọn tối đa {MAX_SEATS_PER_ORDER} ghế.',
            'seat_limit_exceeded',
        )

    expire_stale_orders()
    now = timezone.now()
    expires_at = now + timedelta(minutes=SEAT_HOLD_MINUTES)

    with transaction.atomic():
        seats = list(
            Seat.objects.select_for_update()
            .select_related('event', 'ticket_type')
            .filter(id__in=unique_seat_ids)
            .order_by('id')
        )

        if len(seats) != len(unique_seat_ids):
            raise OrderLifecycleError('Một số ghế được chọn không tồn tại.', 'seat_not_found')

        event_ids = {seat.event_id for seat in seats}
        if len(event_ids) != 1:
            raise OrderLifecycleError(
                'Tất cả ghế trong một đơn phải thuộc cùng một sự kiện.',
                'mixed_events',
            )

        for seat in seats:
            if seat.status == SeatStatusEnum.SOLD:
                raise OrderLifecycleError(f'Ghế {seat.seat_name} đã được bán.', 'seat_sold')

            if seat.status == SeatStatusEnum.LOCKED:
                raise OrderLifecycleError(
                    f'Ghế {seat.seat_name} đang được đơn hàng khác giữ.',
                    'seat_locked',
                )

        total_amount = sum((seat.ticket_type.price for seat in seats), Decimal('0'))
        event = seats[0].event

        order = Order.objects.create(
            customer=customer,
            event=event,
            total_amount=total_amount,
            status=OrderStatusEnum.PENDING,
            expires_at=expires_at,
        )

        OrderItem.objects.bulk_create([
            OrderItem(
                order=order,
                seat=seat,
                ticket_type=seat.ticket_type,
                unit_price=seat.ticket_type.price,
            )
            for seat in seats
        ])

        Seat.objects.filter(id__in=unique_seat_ids).update(
            status=SeatStatusEnum.LOCKED,
            locked_until=expires_at,
            locked_by_order=order,
        )

    return order


@transaction.atomic
def cancel_pending_order(order_id, customer=None):
    queryset = Order.objects.select_for_update()
    if customer is not None:
        queryset = queryset.filter(customer=customer)

    try:
        order = queryset.get(id=order_id)
    except Order.DoesNotExist as exc:
        raise OrderLifecycleError(
            'Không tìm thấy đơn hàng hoặc bạn không có quyền hủy đơn này.',
            'order_not_found',
        ) from exc

    if order.status != OrderStatusEnum.PENDING:
        raise OrderLifecycleError(
            'Chỉ có thể hủy đơn hàng đang chờ thanh toán.',
            'order_not_pending',
        )

    if order.expires_at and order.expires_at <= timezone.now():
        _release_locked_seats(order)
        order.status = OrderStatusEnum.EXPIRED
        order.payos_checkout_url = None
        order.save(update_fields=['status', 'payos_checkout_url', 'updated_at'])
        return order

    _release_locked_seats(order)
    order.status = OrderStatusEnum.CANCELLED
    order.payos_checkout_url = None
    order.save(update_fields=['status', 'payos_checkout_url', 'updated_at'])
    return order

@transaction.atomic
def confirm_order_payment(order_id, amount, transaction_id=None):
    order = Order.objects.select_for_update().get(id=order_id)

    if order.status == OrderStatusEnum.PAID:
        return order, False

    if order.status != OrderStatusEnum.PENDING:
        raise OrderLifecycleError(
            f'Không thể thanh toán đơn hàng ở trạng thái {order.status}.',
            'invalid_payment_state',
        )

    now = timezone.now()
    if order.expires_at and order.expires_at <= now:
        _release_locked_seats(order)
        order.status = OrderStatusEnum.EXPIRED
        order.payos_checkout_url = None
        order.save(update_fields=['status', 'payos_checkout_url', 'updated_at'])
        return order, False

    if transaction_id and Payment.objects.select_for_update().filter(
        transaction_id=str(transaction_id)
    ).exists():
        raise OrderLifecycleError(
            'Mã giao dịch PayOS đã được sử dụng cho giao dịch khác.',
            'duplicate_transaction',
        )

    payment_amount = Decimal(str(amount))
    if payment_amount != order.total_amount:
        raise OrderLifecycleError('Số tiền thanh toán không khớp với đơn hàng.', 'amount_mismatch')

    items = list(order.items.select_related('seat', 'ticket_type').order_by('seat_id'))
    locked_seats = list(
        Seat.objects.select_for_update()
        .filter(
            locked_by_order=order,
            status=SeatStatusEnum.LOCKED,
            id__in=[item.seat_id for item in items],
        )
        .order_by('id')
    )

    if not items or len(locked_seats) != len(items):
        raise OrderLifecycleError(
            'Các ghế của đơn hàng không còn được giữ đầy đủ.',
            'seat_lock_lost',
        )

    Seat.objects.filter(id__in=[seat.id for seat in locked_seats]).update(
        status=SeatStatusEnum.SOLD,
        locked_until=None,
        locked_by_order=None,
    )

    order.status = OrderStatusEnum.PAID
    order.save(update_fields=['status', 'updated_at'])

    Ticket.objects.bulk_create([
        Ticket(
            order=order,
            seat=item.seat,
            ticket_type=item.ticket_type,
            qr_code=f'TK-{order.id}-{item.seat_id}-{uuid.uuid4().hex.upper()}',
        )
        for item in items
    ])

    if transaction_id:
        Payment.objects.create(
            transaction_id=str(transaction_id),
            order=order,
            provider='PAYOS',
            amount=payment_amount,
            status=PaymentStatusEnum.SUCCESS,
        )
    else:
        Payment.objects.create(
            order=order,
            provider='PAYOS',
            amount=payment_amount,
            status=PaymentStatusEnum.SUCCESS,
        )

    return order, True
