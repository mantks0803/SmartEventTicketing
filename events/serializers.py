from rest_framework import serializers
from events.models import Event, TicketType
from seating.models import Seat, SeatStatusEnum

class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = ['id', 'name', 'price', 'total_rows', 'seats_per_row', 'row_prefix']

class EventSerializer(serializers.ModelSerializer):
    ticket_types = TicketTypeSerializer(many=True, read_only=True)
    organizer_name = serializers.CharField(source='organizer.company_name', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'organizer', 'organizer_name', 'title', 'description', 
            'banner_url', 'location', 'start_time', 'end_time', 'status', 
            'created_at', 'ticket_types'
        ]

class TicketTypeInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_rows = serializers.IntegerField(min_value=1)
    seats_per_row = serializers.IntegerField(min_value=1)
    row_prefix = serializers.CharField(max_length=10)

class EventCreateSerializer(serializers.ModelSerializer):
    ticket_types_input = TicketTypeInputSerializer(many=True, write_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'banner_url', 
            'location', 'start_time', 'end_time', 'ticket_types_input'
        ]

    def create(self, validated_data):
        ticket_types_data = validated_data.pop('ticket_types_input')
        organizer = self.context['request'].user.organizer
        
        event = Event.objects.create(organizer=organizer, **validated_data)

        for tt_data in ticket_types_data:
            ticket_type = TicketType.objects.create(event=event, **tt_data)
            
            prefix = tt_data['row_prefix']
            total_rows = tt_data['total_rows']
            seats_per_row = tt_data['seats_per_row']
            
            seats = []
            for r in range(total_rows):
                row_label = f"{prefix}{chr(65 + r)}" if len(prefix) == 1 and prefix.isalpha() else f"{prefix}{r+1}"
                for s in range(1, seats_per_row + 1):
                    seats.append(
                        Seat(
                            event=event,
                            ticket_type=ticket_type,
                            row=row_label,
                            number=str(s),
                            status=SeatStatusEnum.AVAILABLE
                        )
                    )
            Seat.objects.bulk_create(seats)

        return event