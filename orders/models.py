from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

class OrderStatusEnum(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    PAID = 'PAID', 'Paid'
    CANCELLED = 'CANCELLED', 'Cancelled'
    EXPIRED = 'EXPIRED', 'Expired'
    REFUNDED = 'REFUNDED', 'Refunded'

class PaymentStatusEnum(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    SUCCESS = 'SUCCESS', 'Success'
    FAILED = 'FAILED', 'Failed'

class Order(models.Model):
    customer = models.ForeignKey('authentication.Customer', on_delete=models.CASCADE, related_name='orders')
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=OrderStatusEnum.choices, default=OrderStatusEnum.PENDING)
    payos_checkout_url = models.CharField(max_length=500, null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_expired(self):
        return bool(
            self.status == OrderStatusEnum.PENDING
            and self.expires_at
            and self.expires_at <= timezone.now()
        )

    def __str__(self):
        return f"Order #{self.id} - {self.customer.user.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    seat = models.ForeignKey('seating.Seat', on_delete=models.CASCADE, related_name='order_items')
    ticket_type = models.ForeignKey('events.TicketType', on_delete=models.CASCADE, related_name='order_items')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['order', 'seat'], name='unique_seat_per_order')
        ]

    def clean(self):
        errors = {}

        if self.order_id and self.seat_id and self.order.event_id != self.seat.event_id:
            errors['seat'] = 'Ghế phải thuộc cùng sự kiện với đơn hàng.'

        if self.seat_id and self.ticket_type_id and self.seat.ticket_type_id != self.ticket_type_id:
            errors['ticket_type'] = 'Loại vé không khớp với ghế đã chọn.'

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"Order #{self.order_id} - Seat {self.seat.seat_name}"

class Ticket(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tickets')
    seat = models.OneToOneField('seating.Seat', on_delete=models.CASCADE)
    ticket_type = models.ForeignKey('events.TicketType', on_delete=models.CASCADE)
    qr_code = models.CharField(max_length=250, unique=True)
    is_checked_in = models.BooleanField(default=False)
    issued_at = models.DateTimeField(default=timezone.now, editable=False)
    checked_in_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Ticket #{self.id} - Seat {self.seat.row}{self.seat.number}"

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    provider = models.CharField(max_length=50, default='PAYOS')
    transaction_id = models.CharField(max_length=100, null=True, blank=True, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=PaymentStatusEnum.choices, default=PaymentStatusEnum.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment #{self.id} - Order #{self.order.id} ({self.status})"
