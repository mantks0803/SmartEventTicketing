from django.db.models import Sum
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from common.permissions import IsOrganizerPermission
from events.models import Event, TicketType
from events.serializers import EventSerializer, EventCreateSerializer
from orders.models import Order, Ticket
from seating.models import Seat

class EventListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = EventSerializer
    queryset = Event.objects.filter(status='PUBLISHED').order_by('-start_time')

class EventDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = EventSerializer
    queryset = Event.objects.filter(status='PUBLISHED')

class OrganizerEventCreateView(generics.CreateAPIView):
    permission_classes = [IsOrganizerPermission]
    serializer_class = EventCreateSerializer

class OrganizerEventListView(generics.ListAPIView):
    permission_classes = [IsOrganizerPermission]
    serializer_class = EventSerializer

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user.organizer).order_by('-created_at')

class OrganizerDashboardView(APIView):
    permission_classes = [IsOrganizerPermission]

    def get(self, request):
        organizer = request.user.organizer
        events = Event.objects.filter(organizer=organizer)
        total_events = events.count()
        events_ids = list(events.values_list('id', flat=True))

        paid_orders = Order.objects.filter(
            tickets__seat__event_id__in=events_ids,
            status='PAID'
        ).distinct()

        total_revenue = paid_orders.aggregate(total=Sum('total_amount'))['total'] or 0

        total_seats = Seat.objects.filter(event_id__in=events_ids).count()
        sold_seats = Seat.objects.filter(event_id__in=events_ids, status='SOLD').count()
        locked_seats = Seat.objects.filter(event_id__in=events_ids, status='LOCKED').count()
        available_seats = Seat.objects.filter(event_id__in=events_ids, status='AVAILABLE').count()

        tickets = Ticket.objects.filter(seat__event_id__in=events_ids, order__status='PAID')
        total_tickets_sold = tickets.count()
        checked_in_tickets = tickets.filter(is_checked_in=True).count()

        checkin_rate = round((checked_in_tickets / total_tickets_sold * 100), 2) if total_tickets_sold > 0 else 0

        return Response({
            "total_events": total_events,
            "total_revenue": total_revenue,
            "seats_summary": {
                "total": total_seats,
                "sold": sold_seats,
                "locked": locked_seats,
                "available": available_seats
            },
            "checkin_summary": {
                "tickets_sold": total_tickets_sold,
                "checked_in": checked_in_tickets,
                "checkin_rate_percent": checkin_rate
            }
        }, status=status.HTTP_200_OK)