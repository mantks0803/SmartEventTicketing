from django.db import models

class SeatStatusEnum(models.TextChoices):
    AVAILABLE = 'AVAILABLE', 'Available'
    LOCKED = 'LOCKED', 'Locked'
    SOLD = 'SOLD', 'Sold'

class Seat(models.Model):
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='seats')
    ticket_type = models.ForeignKey('events.TicketType', on_delete=models.CASCADE, related_name='seats')
    row = models.CharField(max_length=10)
    number = models.CharField(max_length=10)
    status = models.CharField(max_length=20, choices=SeatStatusEnum.choices, default=SeatStatusEnum.AVAILABLE)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.event.title} - {self.row}{self.number} ({self.status})"