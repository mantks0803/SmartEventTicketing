from rest_framework import serializers
from seating.models import Seat

class SeatSerializer(serializers.ModelSerializer):
    ticket_type_name = serializers.CharField(source='ticket_type.name', read_only=True)
    price = serializers.DecimalField(source='ticket_type.price', max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Seat
        fields = ['id', 'row', 'number', 'status', 'ticket_type', 'ticket_type_name', 'price']