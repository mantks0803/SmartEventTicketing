from django.contrib import admin
from events.models import (
    User, Customer, Organizer, Event, TicketType, 
    Seat, Order, Ticket, KnowledgeBase, ChatSession, ChatMessage
)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'name', 'email', 'phone_number', 'type', 'status')
    list_filter = ('type', 'status')
    search_fields = ('username', 'email', 'name', 'phone_number')

admin.site.register(Customer)
admin.site.register(Organizer)
admin.site.register(Event)
admin.site.register(TicketType)
admin.site.register(Seat)
admin.site.register(Order)
admin.site.register(Ticket)
admin.site.register(KnowledgeBase)
admin.site.register(ChatSession)
admin.site.register(ChatMessage)