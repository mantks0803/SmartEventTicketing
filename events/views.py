from rest_framework import generics, permissions
from .models import Event, EventStatusEnum
from .serializers import EventSerializer, EventCreateSerializer

class EventListView(generics.ListAPIView):
    queryset = Event.objects.filter(status=EventStatusEnum.PUBLISHED).order_by('-created_at')
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]

class EventDetailView(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]

class EventCreateView(generics.CreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

OrganizerEventCreateView = EventCreateView

class OrganizerEventListView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user.organizer).order_by('-created_at')