from rest_framework import generics, permissions
from events.models import Event
from events.serializers import EventListSerializer, EventDetailSerializer, EventCreateSerializer
from common.permissions import IsOrganizerPermission

class EventListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = EventListSerializer

    def get_queryset(self):
        queryset = Event.objects.filter(status='PUBLISHED').order_by('-start_time')
        search_kw = self.request.query_params.get('search', None)
        if search_kw:
            queryset = queryset.filter(title__icontains=search_kw)
        return queryset

class EventDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Event.objects.filter(status='PUBLISHED')
    serializer_class = EventDetailSerializer

class OrganizerEventCreateView(generics.CreateAPIView):
    permission_classes = [IsOrganizerPermission]
    serializer_class = EventCreateSerializer

class OrganizerEventListView(generics.ListAPIView):
    permission_classes = [IsOrganizerPermission]
    serializer_class = EventListSerializer

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user.organizer).order_by('-id')