from django.urls import path
from .views import (
    AdminApproveEventView,
    AdminEventDetailView,
    AdminEventListView,
    AdminRejectEventView,
    EventListView,
    EventDetailView,
    EventCreateView,
    EventThumbnailUploadView,
    OrganizerEventListView,
    EventFeaturedView
)

urlpatterns = [
    path('', EventListView.as_view(), name='event_list'),
    path('featured/', EventFeaturedView.as_view(), name='event_featured'),
    path('create/', EventCreateView.as_view(), name='event_create'),
    path(
        'upload-thumbnail/',
        EventThumbnailUploadView.as_view(),
        name='event_thumbnail_upload',
    ),
    path('organizer/events/', OrganizerEventListView.as_view(), name='organizer_event_list'),
    path('admin/', AdminEventListView.as_view(), name='admin_event_list'),
    path(
        'admin/<int:pk>/',
        AdminEventDetailView.as_view(),
        name='admin_event_detail',
    ),
    path(
        'admin/<int:pk>/approve/',
        AdminApproveEventView.as_view(),
        name='admin_event_approve',
    ),
    path(
        'admin/<int:pk>/reject/',
        AdminRejectEventView.as_view(),
        name='admin_event_reject',
    ),
    path('<int:pk>/', EventDetailView.as_view(), name='event_detail'),
]
