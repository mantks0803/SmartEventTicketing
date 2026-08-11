from django.contrib import admin
from authentication.models import User, Customer, Organizer

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'name', 'email', 'phone_number', 'type', 'status')
    list_filter = ('type', 'status')
    search_fields = ('username', 'email', 'name', 'phone_number')

admin.site.register(Customer)
admin.site.register(Organizer)