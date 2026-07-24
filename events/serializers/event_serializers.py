from rest_framework import serializers
from django.db import transaction
from events.models import Event, TicketType, Seat, Order, Ticket, User,  Organizer


class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = ['id', 'event', 'name', 'price', 'quantity']

class SeatSerializer(serializers.ModelSerializer):
    ticket_type_name = serializers.CharField(source='ticket_type.name', read_only=True)
    price = serializers.DecimalField(source='ticket_type.price', max_digits=12, decimal_places=2, read_only=True)
    class Meta:
        model = Seat
        fields = ['id', 'row', 'number', 'event', 'status','ticket_type','ticket_type_name']

class EventListSerializer(serializers.ModelSerializer):
    organizer_name = serializers.CharField(source='organizer.name', read_only=True)
    min_price = serializers.SerializerMethodField()
    class Meta:
        model = Event
        fields = [
            'id','title', 'banner_url','location','start_time','orgainizer_name','min_price','status'

        ]
        def get_min_price(self, obj):
           ticket_types = obj.ticket_types.all()
           if ticket_types.exists():
                return min(ticket_type.price for ticket_type in ticket_types)
            return 0
class EventDetailSerializer(serializers.ModelSerializer):
    organizer_name = serializers.CharField(source='organizer.company_name', read_only=True)
    ticket_types = TicketTypeSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'banner_url', 'location', 
            'start_time', 'end_time', 'status', 'organizer_name', 'ticket_types'
        ]
    ##5 incomming
class TicketTypeCreateInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_rows = serializers.IntegerField(min_value=1, max_value=26)  #?
    seats_per_row = serializers.IntegerField(min_value=1, max_value=100)  #?
    row_prefix = serializers.CharField(max_length=5, default='A')  #Chữ cái bắt đầu

class EventCreateSerializer(serializers.Serializer):
    
##too tired