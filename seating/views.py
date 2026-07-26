from rest_framework import generics, permissions
from seating.models import Seat
from seating.serializers import SeatSerializer

class EventSeatMatrixView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SeatSerializer

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        return Seat.objects.filter(event_id=event_id).select_related('ticket_type').order_by('row', 'id')