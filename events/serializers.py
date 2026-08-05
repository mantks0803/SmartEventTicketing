from rest_framework import serializers
from .models import Event, TicketType
from seating.models import Seat, SeatStatusEnum

class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = ['id', 'name', 'price', 'quantity']

class EventSerializer(serializers.ModelSerializer):
    ticket_types = TicketTypeSerializer(many=True, read_only=True)
    organizer_name = serializers.CharField(source='organizer.company_name', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'organizer', 'organizer_name', 'title', 'thumbnail',
            'description', 'location', 'start_time', 'category', 'status',
            'created_at', 'ticket_types'
        ]

class TicketTypeInputSerializer(serializers.Serializer):
    name = serializers.CharField()
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_rows = serializers.IntegerField(min_value=1)
    seats_per_row = serializers.IntegerField(min_value=1)
    row_prefix = serializers.CharField(default='A')

class EventCreateSerializer(serializers.ModelSerializer):
    ticket_types = TicketTypeInputSerializer(many=True, write_only=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'thumbnail', 'description', 'location', 'start_time', 'category', 'ticket_types']

    def create(self, validated_data):
        ticket_types_data = validated_data.pop('ticket_types')
        organizer = self.context['request'].user.organizer

        event = Event.objects.create(organizer=organizer, **validated_data)

        for tt_data in ticket_types_data:
            total_rows = tt_data.pop('total_rows')
            seats_per_row = tt_data.pop('seats_per_row')
            row_prefix = tt_data.pop('row_prefix', 'A')

            quantity = total_rows * seats_per_row

            ticket_type = TicketType.objects.create(
                event=event,
                name=tt_data['name'],
                price=tt_data['price'],
                quantity=quantity
            )

            seats_to_create = []
            for row_idx in range(total_rows):
                row_label = f"{row_prefix}{row_idx + 1}"
                for seat_num in range(1, seats_per_row + 1):
                    seats_to_create.append(
                        Seat(
                            event=event,
                            ticket_type=ticket_type,
                            row=row_label,
                            number=seat_num,
                            seat_name=f"{row_label}-{seat_num}",
                            status=SeatStatusEnum.AVAILABLE
                        )
                    )
            Seat.objects.bulk_create(seats_to_create)

        return event