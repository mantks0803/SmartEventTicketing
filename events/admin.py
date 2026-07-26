from django.contrib import admin
from events.models import Event, TicketType

admin.site.register(Event)
admin.site.register(TicketType)