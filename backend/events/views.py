import cloudinary.uploader
from django.db.models import Q
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.permissions import IsAdminPermission, IsOrganizerPermission
from .models import Event, EventStatusEnum
from .serializers import (
    EventCreateSerializer,
    EventSerializer,
    EventThumbnailUploadSerializer,
)


class EventPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class EventListView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = EventPagination

    def get_queryset(self):
        queryset = (
            Event.objects
            .filter(status=EventStatusEnum.PUBLISHED)
            .order_by('-created_at')
        )

        category = self.request.query_params.get('category')
        search = self.request.query_params.get('search')

        if category and category != 'ALL':
            queryset = queryset.filter(category=category)

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(location__icontains=search)
            )

        return queryset


class EventDetailView(generics.RetrieveAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Event.objects.filter(
            status=EventStatusEnum.PUBLISHED
        )


class EventCreateView(generics.CreateAPIView):
    serializer_class = EventCreateSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsOrganizerPermission
    ]


class EventThumbnailUploadView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        IsOrganizerPermission,
    ]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = EventThumbnailUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            upload_result = cloudinary.uploader.upload(
                serializer.validated_data['thumbnail'],
                folder='smartticket_events',
                resource_type='image',
                allowed_formats=['jpg', 'jpeg', 'png', 'webp'],
            )
        except Exception:
            return Response(
                {
                    'error': 'Không thể tải ảnh lên Cloudinary.',
                    'code': 'thumbnail_upload_failed',
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        secure_url = upload_result.get('secure_url')
        if not secure_url:
            return Response(
                {
                    'error': 'Cloudinary không trả về đường dẫn ảnh.',
                    'code': 'thumbnail_upload_failed',
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {'secure_url': secure_url},
            status=status.HTTP_201_CREATED,
        )


# Giữ lại tên cũ để không ảnh hưởng import hiện tại.
OrganizerEventCreateView = EventCreateView


class OrganizerEventListView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsOrganizerPermission
    ]

    def get_queryset(self):
        return (
            Event.objects
            .filter(organizer=self.request.user.organizer)
            .prefetch_related('ticket_types')
            .order_by('-created_at')
        )


class EventFeaturedView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return (
            Event.objects
            .filter(
                status=EventStatusEnum.PUBLISHED,
                start_time__gte=timezone.now()
            )
            .order_by('start_time')[:8]
        )


class AdminEventListView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsAdminPermission,
    ]
    pagination_class = EventPagination

    def list(self, request, *args, **kwargs):
        status_value = request.query_params.get('status')

        if (
            status_value
            and status_value.upper() not in EventStatusEnum.values
        ):
            return Response(
                {
                    'error': 'Trạng thái sự kiện không hợp lệ.',
                    'code': 'invalid_status',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = (
            Event.objects
            .select_related('organizer')
            .prefetch_related('ticket_types')
            .order_by('-created_at')
        )

        status_value = self.request.query_params.get('status')
        search = self.request.query_params.get('search')

        if status_value:
            queryset = queryset.filter(status=status_value.upper())

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(location__icontains=search)
                | Q(organizer__company_name__icontains=search)
            )

        return queryset


class AdminEventDetailView(generics.RetrieveAPIView):
    serializer_class = EventSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsAdminPermission,
    ]

    def get_queryset(self):
        return (
            Event.objects
            .select_related('organizer')
            .prefetch_related('ticket_types')
        )


class AdminApproveEventView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        IsAdminPermission,
    ]

    def post(self, request, pk):
        with transaction.atomic():
            # Khóa event để tránh hai admin xử lý cùng lúc.
            event = get_object_or_404(
                Event.objects.select_for_update(),
                pk=pk,
            )

            if event.status != EventStatusEnum.PENDING:
                return Response(
                    {
                        'error': 'Chỉ có thể duyệt sự kiện đang chờ duyệt.',
                        'code': 'event_not_pending',
                    },
                    status=status.HTTP_409_CONFLICT,
                )

            if event.start_time <= timezone.now():
                return Response(
                    {
                        'error': 'Không thể duyệt sự kiện đã qua giờ bắt đầu.',
                        'code': 'event_already_started',
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            event.status = EventStatusEnum.PUBLISHED
            event.save(update_fields=['status', 'updated_at'])

        return Response({
            'message': 'Đã duyệt sự kiện thành công.',
            'event': EventSerializer(event).data,
        })


class AdminRejectEventView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        IsAdminPermission,
    ]

    def post(self, request, pk):
        with transaction.atomic():
            # Khóa event để tránh hai admin xử lý cùng lúc.
            event = get_object_or_404(
                Event.objects.select_for_update(),
                pk=pk,
            )

            if event.status != EventStatusEnum.PENDING:
                return Response(
                    {
                        'error': 'Chỉ có thể từ chối sự kiện đang chờ duyệt.',
                        'code': 'event_not_pending',
                    },
                    status=status.HTTP_409_CONFLICT,
                )

            event.status = EventStatusEnum.CANCELLED
            event.save(update_fields=['status', 'updated_at'])

        return Response({
            'message': 'Đã từ chối sự kiện.',
            'event': EventSerializer(event).data,
        })
