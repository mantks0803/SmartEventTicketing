from rest_framework import generics, permissions
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .models import Event, EventStatusEnum
from .serializers import EventSerializer, EventCreateSerializer

class EventPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100

class EventListView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = EventPagination

    def get_queryset(self):
        queryset = Event.objects.filter(status=EventStatusEnum.PUBLISHED).order_by('-created_at')
        category = self.request.query_params.get('category')
        search = self.request.query_params.get('search')

        if category and category != 'ALL':
            queryset = queryset.filter(category=category)

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(location__icontains=search)
            )

        return queryset

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

class EventFeaturedView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Event.objects.filter(status=EventStatusEnum.PUBLISHED).order_by('start_time')[:8]