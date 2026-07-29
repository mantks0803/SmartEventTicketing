from django.contrib import admin
from orders.models import Order, Ticket, Payment

admin.site.register(Order)
admin.site.register(Ticket)
admin.site.register(Payment)