from django.urls import path
from events.views import (
    EventListView, EventDetailView, 
    OrganizerEventCreateView, OrganizerEventListView, OrganizerDashboardView
)

urlpatterns = [
    path('', EventListView.as_view(), name='event_list'),
    path('<int:pk>/', EventDetailView.as_view(), name='event_detail'),
    path('organizer/create/', OrganizerEventCreateView.as_view(), name='organizer_create_event'),
    path('organizer/my-events/', OrganizerEventListView.as_view(), name='organizer_my_events'),
    path('organizer/dashboard/', OrganizerDashboardView.as_view(), name='organizer_dashboard'),
]