from django.db import models
from events.models import Event, TicketType

class SeatStatusEnum(models.TextChoices):
    AVAILABLE = 'AVAILABLE', 'Available'
    LOCKED = 'LOCKED', 'Locked'
    SOLD = 'SOLD', 'Sold'

class Seat(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='seats')
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE, related_name='seats')
    row = models.CharField(max_length=20, default='A')
    number = models.IntegerField(default=1)
    seat_name = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=SeatStatusEnum.choices, default=SeatStatusEnum.AVAILABLE)
    locked_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('event', 'row', 'number')

    def save(self, *args, **kwargs):
        if not self.seat_name:
            self.seat_name = f"{self.row}-{self.number}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.event.title} - {self.row}{self.number} ({self.status})"