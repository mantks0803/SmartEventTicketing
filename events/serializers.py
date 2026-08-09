from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from .models import Event, TicketType
from seating.models import Seat, SeatStatusEnum


MAX_SEATS_PER_EVENT = 5000


class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = ['id', 'name', 'price', 'quantity']


class EventSerializer(serializers.ModelSerializer):
    ticket_types = TicketTypeSerializer(many=True, read_only=True)
    organizer_name = serializers.CharField(
        source='organizer.company_name',
        read_only=True
    )

    class Meta:
        model = Event
        fields = [
            'id', 'organizer', 'organizer_name', 'title', 'thumbnail',
            'description', 'location', 'start_time', 'category', 'status',
            'created_at', 'ticket_types'
        ]


class TicketTypeInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=1000
    )
    total_rows = serializers.IntegerField(
        min_value=1,
        max_value=50
    )
    seats_per_row = serializers.IntegerField(
        min_value=1,
        max_value=100
    )
    row_prefix = serializers.RegexField(
        regex=r'^[A-Za-z0-9]+$',
        max_length=10,
        error_messages={
            'invalid': 'Tiền tố hàng chỉ được chứa chữ cái và chữ số.'
        }
    )


class EventCreateSerializer(serializers.ModelSerializer):
    thumbnail = serializers.URLField()
    ticket_types = TicketTypeInputSerializer(
        many=True,
        write_only=True,
        allow_empty=False
    )

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'thumbnail', 'description',
            'location', 'start_time', 'category', 'ticket_types'
        ]

    def validate_start_time(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError(
                'Thời gian bắt đầu phải ở tương lai.'
            )
        return value

    def validate_ticket_types(self, value):
        ticket_names = set()
        row_names = set()
        total_seats = 0

        for ticket_type in value:
            name = ticket_type['name'].strip()
            normalized_name = name.lower()

            if normalized_name in ticket_names:
                raise serializers.ValidationError(
                    f'Loại vé "{name}" đang bị trùng.'
                )

            ticket_names.add(normalized_name)
            ticket_type['name'] = name

            prefix = ticket_type['row_prefix'].strip().upper()
            ticket_type['row_prefix'] = prefix

            total_rows = ticket_type['total_rows']
            seats_per_row = ticket_type['seats_per_row']

            for row_index in range(total_rows):
                row_name = f'{prefix}{row_index + 1}'

                if row_name in row_names:
                    raise serializers.ValidationError(
                        f'Hàng ghế "{row_name}" đang bị trùng giữa các loại vé.'
                    )

                row_names.add(row_name)

            total_seats += total_rows * seats_per_row

        if total_seats > MAX_SEATS_PER_EVENT:
            raise serializers.ValidationError(
                f'Mỗi sự kiện chỉ được tạo tối đa '
                f'{MAX_SEATS_PER_EVENT} ghế.'
            )

        return value

    @transaction.atomic
    def create(self, validated_data):
        ticket_types_data = validated_data.pop('ticket_types')
        organizer = self.context['request'].user.organizer

        event = Event.objects.create(
            organizer=organizer,
            **validated_data
        )

        for ticket_data in ticket_types_data:
            total_rows = ticket_data['total_rows']
            seats_per_row = ticket_data['seats_per_row']
            row_prefix = ticket_data['row_prefix']

            quantity = total_rows * seats_per_row

            ticket_type = TicketType.objects.create(
                event=event,
                name=ticket_data['name'],
                price=ticket_data['price'],
                quantity=quantity
            )

            seats = []

            for row_index in range(total_rows):
                row_name = f'{row_prefix}{row_index + 1}'

                for seat_number in range(1, seats_per_row + 1):
                    seats.append(
                        Seat(
                            event=event,
                            ticket_type=ticket_type,
                            row=row_name,
                            number=seat_number,
                            seat_name=f'{row_name}-{seat_number}',
                            status=SeatStatusEnum.AVAILABLE
                        )
                    )

            Seat.objects.bulk_create(seats)

        return event