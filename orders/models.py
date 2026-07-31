from django.db import models

class OrderStatusEnum(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    PAID = 'PAID', 'Paid'
    CANCELLED = 'CANCELLED', 'Cancelled'
    REFUNDED = 'REFUNDED', 'Refunded'

class PaymentStatusEnum(models.TextChoices):
    SUCCESS = 'SUCCESS', 'Success'
    FAILED = 'FAILED', 'Failed'

class Order(models.Model):
    customer = models.ForeignKey('authentication.Customer', on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=OrderStatusEnum.choices, default=OrderStatusEnum.PENDING)
    payos_checkout_url = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer.user.name}"

class Ticket(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tickets')
    seat = models.OneToOneField('seating.Seat', on_delete=models.CASCADE)
    ticket_type = models.ForeignKey('events.TicketType', on_delete=models.CASCADE)
    qr_code = models.CharField(max_length=250, unique=True)
    is_checked_in = models.BooleanField(default=False)

    def __str__(self):
        return f"Ticket #{self.id} - Seat {self.seat.row}{self.seat.number}"

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    provider = models.CharField(max_length=50, default='PAYOS')
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=PaymentStatusEnum.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment #{self.id} - Order #{self.order.id} ({self.status})"