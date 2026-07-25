from rest_framework import generics, permissions, status
from rest_framework.response import Response
from events.models import Event, Seat
from events.serializers import (
    EventListSerializer, EventDetailSerializer, 
    EventCreateSerializer, SeatSerializer
)



class IsOrganizerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.type == 'ORGANIZER'
        )



class EventListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = EventListSerializer

    def get_queryset(self):
        # Chỉ hiển thị các sự kiện đã được Admin duyệt (PUBLISHED)
        queryset = Event.objects.filter(status='PUBLISHED').order_by('-start_time')
        
        # Hỗ trợ tìm kiếm theo từ khóa 'search' từ query params
        search_kw = self.request.query_params.get('search', None)
        if search_kw:
            queryset = queryset.filter(title__icontains=search_kw)
            
        return queryset



class EventDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Event.objects.filter(status='PUBLISHED')
    serializer_class = EventDetailSerializer



class EventSeatMatrixView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SeatSerializer

    def get_queryset(self):
        event_id = self.kwargs.get('pk')
        # Lấy toàn bộ danh sách ghế của sự kiện, sắp xếp theo hàng và số ghế
        return Seat.objects.filter(event_id=event_id).select_related('ticket_type').order_by('row', 'id')



class OrganizerEventCreateView(generics.CreateAPIView):
    permission_classes = [IsOrganizerPermission]
    serializer_class = EventCreateSerializer



class OrganizerEventListView(generics.ListAPIView):
    permission_classes = [IsOrganizerPermission]
    serializer_class = EventListSerializer

    def get_queryset(self):
        # Lấy danh sách show thuộc về Organizer đang đăng nhập
        return Event.objects.filter(organizer=self.request.user.organizer).order_by('-id')