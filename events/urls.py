from django.urls import path
from .views import (
    EventListView,
    EventDetailView,
    EventCreateView,
    OrganizerEventCreateView,
    OrganizerEventListView,
    EventFeaturedView
)

urlpatterns = [
    path('', EventListView.as_view(), name='event_list'),
    path('featured/', EventFeaturedView.as_view(), name='event_featured'),
    path('<int:pk>/', EventDetailView.as_view(), name='event_detail'),
    path('create/', EventCreateView.as_view(), name='event_create'),
    path('organizer/events/', OrganizerEventListView.as_view(), name='organizer_event_list'),
]