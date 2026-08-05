from django.utils import timezone
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from seating.models import Seat, SeatStatusEnum
from seating.serializers import SeatSerializer
from orders.models import Order, OrderStatusEnum, Ticket

class EventSeatMatrixView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, event_id):
        seats = Seat.objects.filter(event_id=event_id).select_related('ticket_type')
        serializer = SeatSerializer(seats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ReleaseExpiredSeatsView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        now = timezone.now()

        with transaction.atomic():
            expired_seats = Seat.objects.select_for_update().filter(
                status=SeatStatusEnum.LOCKED,
                locked_until__lt=now
            )

            if expired_seats.exists():
                seat_ids = list(expired_seats.values_list('id', flat=True))

                order_ids = Ticket.objects.filter(
                    seat_id__in=seat_ids,
                    order__status=OrderStatusEnum.PENDING
                ).values_list('order_id', flat=True).distinct()

                Order.objects.filter(id__in=list(order_ids)).update(status=OrderStatusEnum.CANCELLED)

                expired_seats.update(status=SeatStatusEnum.AVAILABLE, locked_until=None)

        return Response({'message': 'Đã nhả các ghế hết hạn và cập nhật đơn hàng thành công.'})