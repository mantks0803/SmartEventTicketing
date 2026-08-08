from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from seating.models import Seat
from seating.serializers import SeatSerializer
from orders.services import expire_stale_orders

class EventSeatMatrixView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, event_id):
        expire_stale_orders()
        seats = (
            Seat.objects.filter(event_id=event_id)
            .select_related('ticket_type')
            .order_by('ticket_type_id', 'row', 'number')
        )
        serializer = SeatSerializer(seats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ReleaseExpiredSeatsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        expired_count = expire_stale_orders()
        return Response({
            'message': 'Đã xử lý các đơn hàng hết hạn.',
            'expired_orders': expired_count,
        })
