from django.urls import path
from seating.views import EventSeatMatrixView

urlpatterns = [
    path('event/<int:event_id>/', EventSeatMatrixView.as_view(), name='event_seats'),
]