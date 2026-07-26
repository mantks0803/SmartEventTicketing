from rest_framework import serializers
from django.db import transaction
from events.models import Event, TicketType
from seating.models import Seat  # Import Seat từ app seating

class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = ['id', 'name', 'price', 'quantity']

class EventListSerializer(serializers.ModelSerializer):
    organizer_name = serializers.CharField(source='organizer.company_name', read_only=True)
    min_price = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'title', 'banner_url', 'location', 'start_time', 'organizer_name', 'min_price', 'status']

    def get_min_price(self, obj):
        ticket_types = obj.ticket_types.all()
        if ticket_types.exists():
            return min(tt.price for tt in ticket_types)
        return 0

class EventDetailSerializer(serializers.ModelSerializer):
    organizer_name = serializers.CharField(source='organizer.company_name', read_only=True)
    ticket_types = TicketTypeSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'banner_url', 'location', 'start_time', 'end_time', 'status', 'organizer_name', 'ticket_types']

class TicketTypeCreateInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_rows = serializers.IntegerField(min_value=1, max_value=26)
    seats_per_row = serializers.IntegerField(min_value=1, max_value=50)
    row_prefix = serializers.CharField(max_length=5, default="A")

class EventCreateSerializer(serializers.ModelSerializer):
    ticket_types_input = TicketTypeCreateInputSerializer(many=True, write_only=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'banner_url', 'location', 'start_time', 'end_time', 'ticket_types_input']

    @transaction.atomic
    def create(self, validated_data):
        ticket_types_data = validated_data.pop('ticket_types_input')
        request = self.context.get('request')
        organizer = request.user.organizer

        event = Event.objects.create(organizer=organizer, status='PENDING', **validated_data)

        for tt_data in ticket_types_data:
            name = tt_data['name']
            price = tt_data['price']
            total_rows = tt_data['total_rows']
            seats_per_row = tt_data['seats_per_row']
            prefix = tt_data.get('row_prefix', 'A').upper()

            quantity = total_rows * seats_per_row

            ticket_type = TicketType.objects.create(
                event=event,
                name=name,
                price=price,
                quantity=quantity
            )

            seats_to_create = []
            for r_idx in range(total_rows):
                base_char_code = ord(prefix[0]) if prefix else ord('A')
                row_label = chr(base_char_code + r_idx)
                
                for c_num in range(1, seats_per_row + 1):
                    seats_to_create.append(
                        Seat(
                            event=event,
                            ticket_type=ticket_type,
                            row=row_label,
                            number=str(c_num),
                            status='AVAILABLE'
                        )
                    )
            Seat.objects.bulk_create(seats_to_create)

        return event