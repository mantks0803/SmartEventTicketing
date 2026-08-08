from rest_framework import serializers
from orders.models import Order, OrderItem, Ticket
from orders.services import MAX_SEATS_PER_ORDER
from seating.serializers import SeatSerializer

class TicketSerializer(serializers.ModelSerializer):
    seat_details = SeatSerializer(source='seat', read_only=True)
    ticket_type_name = serializers.CharField(source='ticket_type.name', read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'seat', 'seat_details', 'ticket_type_name', 'qr_code', 'is_checked_in']


class OrderItemSerializer(serializers.ModelSerializer):
    seat_details = SeatSerializer(source='seat', read_only=True)
    ticket_type_name = serializers.CharField(source='ticket_type.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'seat', 'seat_details', 'ticket_type',
            'ticket_type_name', 'unit_price'
        ]

class CustomerTicketSerializer(serializers.ModelSerializer):
    seat_row = serializers.CharField(source='seat.row', read_only=True)
    seat_number = serializers.IntegerField(source='seat.number', read_only=True)
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
    items = OrderItemSerializer(many=True, read_only=True)
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'event', 'total_amount', 'status',
            'expires_at', 'created_at', 'updated_at', 'items', 'tickets'
        ]

class HoldSeatsInputSerializer(serializers.Serializer):
    seat_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        max_length=MAX_SEATS_PER_ORDER,
    )

    def validate_seat_ids(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError('Danh sách ghế không được chứa ID trùng lặp.')
        return value

class CheckInInputSerializer(serializers.Serializer):
    qr_code = serializers.CharField(max_length=250)
