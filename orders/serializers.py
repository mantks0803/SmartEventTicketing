from rest_framework import serializers

from orders.models import Order, OrderItem, Ticket
from orders.services import MAX_SEATS_PER_ORDER
from seating.serializers import SeatSerializer


class TicketSerializer(serializers.ModelSerializer):
    seat_details = SeatSerializer(source='seat', read_only=True)
    ticket_type_name = serializers.CharField(
        source='ticket_type.name',
        read_only=True,
    )

    class Meta:
        model = Ticket
        fields = [
            'id', 'seat', 'seat_details', 'ticket_type_name',
            'qr_code', 'is_checked_in', 'issued_at', 'checked_in_at',
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    seat_details = SeatSerializer(source='seat', read_only=True)
    ticket_type_name = serializers.CharField(
        source='ticket_type.name',
        read_only=True,
    )

    class Meta:
        model = OrderItem
        fields = [
            'id', 'seat', 'seat_details', 'ticket_type',
            'ticket_type_name', 'unit_price',
        ]


class CustomerTicketSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    event_id = serializers.IntegerField(source='seat.event.id', read_only=True)
    event_title = serializers.CharField(
        source='seat.event.title',
        read_only=True,
    )
    event_thumbnail = serializers.CharField(
        source='seat.event.thumbnail',
        read_only=True,
    )
    event_location = serializers.CharField(
        source='seat.event.location',
        read_only=True,
    )
    event_start_time = serializers.DateTimeField(
        source='seat.event.start_time',
        read_only=True,
    )
    seat_name = serializers.CharField(source='seat.seat_name', read_only=True)
    seat_row = serializers.CharField(source='seat.row', read_only=True)
    seat_number = serializers.IntegerField(source='seat.number', read_only=True)
    ticket_type_name = serializers.CharField(
        source='ticket_type.name',
        read_only=True,
    )
    price = serializers.SerializerMethodField()

    def get_price(self, ticket):
        for item in ticket.order.items.all():
            if item.seat_id == ticket.seat_id:
                return str(item.unit_price)
        return str(ticket.ticket_type.price)

    class Meta:
        model = Ticket
        fields = [
            'id', 'order_id', 'event_id', 'event_title', 'event_thumbnail',
            'event_location', 'event_start_time', 'seat_name', 'seat_row',
            'seat_number', 'ticket_type_name', 'price', 'qr_code',
            'is_checked_in', 'issued_at', 'checked_in_at',
        ]


class OrderSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)
    event_thumbnail = serializers.CharField(
        source='event.thumbnail',
        read_only=True,
    )
    items = OrderItemSerializer(many=True, read_only=True)
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'event', 'event_title', 'event_thumbnail',
            'total_amount', 'status', 'expires_at', 'created_at',
            'updated_at', 'items', 'tickets',
        ]


class HoldSeatsInputSerializer(serializers.Serializer):
    seat_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        max_length=MAX_SEATS_PER_ORDER,
    )

    def validate_seat_ids(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                'Danh sách ghế không được chứa ID trùng lặp.'
            )
        return value


class CheckInInputSerializer(serializers.Serializer):
    qr_code = serializers.CharField(max_length=250)
