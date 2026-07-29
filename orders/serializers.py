from rest_framework import serializers
from orders.models import Order, Ticket
from seating.serializers import SeatSerializer

class TicketSerializer(serializers.ModelSerializer):
    seat_details = SeatSerializer(source='seat', read_only=True)
    ticket_type_name = serializers.CharField(source='ticket_type.name', read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'seat', 'seat_details', 'ticket_type_name', 'qr_code', 'is_checked_in']

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

