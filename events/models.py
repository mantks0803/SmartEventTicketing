from django.db import models
from authentication.models import Organizer

class EventCategoryEnum(models.TextChoices):
    MUSIC = 'MUSIC', 'Music'
    WORKSHOP = 'WORKSHOP', 'Workshop'
    ENTERTAINMENT = 'ENTERTAINMENT', 'Entertainment'
    SPORTS = 'SPORTS', 'Sports'

class EventStatusEnum(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    PUBLISHED = 'PUBLISHED', 'Published'
    CANCELLED = 'CANCELLED', 'Cancelled'

class Event(models.Model):
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=250)
    thumbnail = models.CharField(max_length=500)
    description = models.TextField()
    location = models.CharField(max_length=250)
    start_time = models.DateTimeField()
    category = models.CharField(max_length=50, choices=EventCategoryEnum.choices, default=EventCategoryEnum.MUSIC)
    status = models.CharField(max_length=20, choices=EventStatusEnum.choices, default=EventStatusEnum.PUBLISHED)
    is_payout_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class TicketType(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_types')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.event.title} - {self.name}"