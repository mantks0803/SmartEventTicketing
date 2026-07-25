from django.urls import path
from events.views import (
    RegisterView, CustomTokenObtainPairView,
    EventListView, EventDetailView, EventSeatMatrixView,
    OrganizerEventCreateView, OrganizerEventListView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('events/', EventListView.as_view(), name='event_list'),
    path('events/<int:pk>/', EventDetailView.as_view(), name='event_detail'),
    path('events/<int:pk>/seats/', EventSeatMatrixView.as_view(), name='event_seats'),

    path('organizer/events/', OrganizerEventListView.as_view(), name='organizer_event_list'),
    path('organizer/events/create/', OrganizerEventCreateView.as_view(), name='organizer_event_create'),
]