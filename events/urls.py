from django.urls import path
from events.views import EventListView, EventDetailView, OrganizerEventCreateView, OrganizerEventListView

urlpatterns = [
    # Public
    path('', EventListView.as_view(), name='event_list'),
    path('<int:pk>/', EventDetailView.as_view(), name='event_detail'),
    
    # Organizer
    path('organizer/list/', OrganizerEventListView.as_view(), name='organizer_event_list'),
    path('organizer/create/', OrganizerEventCreateView.as_view(), name='organizer_event_create'),
]