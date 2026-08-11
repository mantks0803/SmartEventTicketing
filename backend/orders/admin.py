from django.contrib import admin
from orders.models import Order, OrderItem, Payment, Ticket


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('seat', 'ticket_type', 'unit_price', 'created_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'event', 'total_amount', 'status', 'expires_at', 'created_at')
    list_filter = ('status', 'event')
    search_fields = ('id', 'customer__user__username', 'customer__user__email', 'event__title')
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'seat', 'ticket_type', 'unit_price')
    search_fields = ('order__id', 'seat__seat_name', 'order__customer__user__username')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'seat', 'is_checked_in', 'issued_at', 'checked_in_at')
    list_filter = ('is_checked_in', 'ticket_type')
    search_fields = ('qr_code', 'order__id', 'seat__seat_name')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'provider', 'transaction_id', 'amount', 'status', 'created_at')
    list_filter = ('provider', 'status')
    search_fields = ('transaction_id', 'order__id')
