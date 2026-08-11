from django.contrib import admin
from seating.models import Seat


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'event', 'seat_name', 'ticket_type',
        'status', 'locked_by_order', 'locked_until'
    )
    list_filter = ('status', 'event', 'ticket_type')
    search_fields = ('seat_name', 'event__title')
