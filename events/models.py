from django.db import models

class EventStatusEnum(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    PUBLISHED = 'PUBLISHED', 'Published'
    REJECTED = 'REJECTED', 'Rejected'
    CANCELLED = 'CANCELLED', 'Cancelled'
    COMPLETED = 'COMPLETED', 'Completed'

class Event(models.Model):
    organizer = models.ForeignKey('authentication.Organizer', on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=250)
    description = models.TextField()
    banner_url = models.CharField(max_length=500)
    location = models.CharField(max_length=250) 
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=EventStatusEnum.choices, default=EventStatusEnum.PENDING)

    def __str__(self):
        return self.title

class TicketType(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_types')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.name} - {self.event.title}"