from django.urls import path
from seating.views import EventSeatMatrixView, ReleaseExpiredSeatsView

urlpatterns = [
    path('event/<int:event_id>/', EventSeatMatrixView.as_view(), name='event_seats'),
    path('release-expired/', ReleaseExpiredSeatsView.as_view(), name='release_expired_seats'),
]