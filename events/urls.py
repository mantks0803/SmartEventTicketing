from django.urls import path
from .views import (
    EventListView,
    EventDetailView,
    EventCreateView,
    OrganizerEventCreateView,
    OrganizerEventListView
)

urlpatterns = [
    path('', EventListView.as_view(), name='event_list'),
    path('<int:pk>/', EventDetailView.as_view(), name='event_detail'),
    path('create/', EventCreateView.as_view(), name='event_create'),
    path('organizer/events/', OrganizerEventListView.as_view(), name='organizer_event_list'),
]