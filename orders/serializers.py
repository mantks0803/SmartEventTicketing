from rest_framework import serializers
from orders.models import Order, Ticket
from seating.serializers import SeatSerializer

class TicketSerializer(serializers.ModelSerializer):
    seat_details = SeatSerializer(source='seat', read_only=True)
    ticket_type_name = serializers.CharField(source='ticket_type.name', read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'seat', 'seat_details', 'ticket_type_name', 'qr_code', 'is_checked_in']

class CustomerTicketSerializer(serializers.ModelSerializer):
    seat_row = serializers.CharField(source='seat.row', read_only=True)
    seat_number = serializers.CharField(source='seat.number', read_only=True)
    event_title = serializers.CharField(source='seat.event.title', read_only=True)
    event_location = serializers.CharField(source='seat.event.location', read_only=True)
    event_start_time = serializers.DateTimeField(source='seat.event.start_time', read_only=True)
    ticket_type_name = serializers.CharField(source='ticket_type.name', read_only=True)
    price = serializers.DecimalField(source='ticket_type.price', max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'event_title', 'event_location', 'event_start_time',
            'seat_row', 'seat_number', 'ticket_type_name', 'price',
            'qr_code', 'is_checked_in'
        ]

class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'total_amount', 'status', 'created_at', 'tickets']

class HoldSeatsInputSerializer(serializers.Serializer):
    seat_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )

class CheckInInputSerializer(serializers.Serializer):
    qr_code = serializers.CharField(max_length=250)