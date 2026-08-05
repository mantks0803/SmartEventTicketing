import uuid
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from orders.models import Order, OrderStatusEnum, Ticket
from orders.serializers import (
    OrderSerializer, CustomerTicketSerializer, 
    HoldSeatsInputSerializer, CheckInInputSerializer
)
from seating.models import Seat, SeatStatusEnum
from authentication.permissions import IsCustomerPermission
from .utils import send_payment_success_email

class HoldSeatsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerPermission]

    def post(self, request):
        serializer = HoldSeatsInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        seat_ids = serializer.validated_data['seat_ids']
        customer = getattr(request.user, 'customer', None)
        if not customer:
            return Response({'error': 'Tài khoản không phải là khách hàng.'}, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        lock_duration = timedelta(minutes=10)

        try:
            with transaction.atomic():
                seats = Seat.objects.select_for_update().filter(id__in=seat_ids)
                if seats.count() != len(seat_ids):
                    return Response({'error': 'Một số ghế chọn không tồn tại.'}, status=status.HTTP_400_BAD_REQUEST)

                for seat in seats:
                    if seat.status == SeatStatusEnum.SOLD:
                        return Response({'error': f'Ghế {seat.seat_name} đã được bán.'}, status=status.HTTP_400_BAD_REQUEST)
                    if seat.status == SeatStatusEnum.LOCKED and seat.locked_until and seat.locked_until > now:
                        return Response({'error': f'Ghế {seat.seat_name} đang được người khác giữ.'}, status=status.HTTP_400_BAD_REQUEST)

                event = seats.first().event
                total_amount = sum(s.ticket_type.price for s in seats)

                order = Order.objects.create(
                    customer=customer,
                    event=event,
                    total_amount=total_amount,
                    status=OrderStatusEnum.PENDING
                )

                seats.update(status=SeatStatusEnum.LOCKED, locked_until=now + lock_duration)

                tickets_to_create = []
                for seat in seats:
                    tickets_to_create.append(
                        Ticket(
                            order=order,
                            seat=seat,
                            ticket_type=seat.ticket_type,
                            qr_code=f"TK-{order.id}-{seat.id}-{uuid.uuid4().hex[:8].upper()}"
                        )
                    )
                Ticket.objects.bulk_create(tickets_to_create)

            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CustomerOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerPermission]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user.customer).order_by('-created_at')

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.all()

class CancelOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            with transaction.atomic():
                order = Order.objects.select_for_update().get(id=pk)
                if order.status != OrderStatusEnum.PENDING:
                    return Response({'error': 'Chỉ có thể hủy đơn hàng đang chờ thanh toán.'}, status=status.HTTP_400_BAD_REQUEST)

                order.status = OrderStatusEnum.CANCELLED
                order.save()

                tickets = Ticket.objects.filter(order=order)
                seat_ids = tickets.values_list('seat_id', flat=True)
                Seat.objects.filter(id__in=seat_ids).update(status=SeatStatusEnum.AVAILABLE, locked_until=None)

            return Response({'message': 'Đã hủy đơn hàng thành công.'}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'error': 'Không tìm thấy đơn hàng.'}, status=status.HTTP_404_NOT_FOUND)

class CreatePayOSPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, customer=request.user.customer)
            if order.status != OrderStatusEnum.PENDING:
                return Response({'error': 'Đơn hàng không ở trạng thái chờ thanh toán.'}, status=status.HTTP_400_BAD_REQUEST)

            checkout_url = f"{settings.FRONTEND_URL}/payment-mock/{order.id}"
            order.payos_checkout_url = checkout_url
            order.save()

            return Response({'checkoutUrl': checkout_url}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'error': 'Không tìm thấy đơn hàng.'}, status=status.HTTP_404_NOT_FOUND)

class CustomerTicketListView(generics.ListAPIView):
    serializer_class = CustomerTicketSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerPermission]

    def get_queryset(self):
        return Ticket.objects.filter(order__customer=self.request.user.customer, order__status=OrderStatusEnum.PAID).order_by('-id')

class CheckInView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CheckInInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        qr_code = serializer.validated_data['qr_code']
        try:
            ticket = Ticket.objects.get(qr_code=qr_code)
            if ticket.is_checked_in:
                return Response({'error': 'Vé này đã được soát vé trước đó!'}, status=status.HTTP_400_BAD_REQUEST)

            ticket.is_checked_in = True
            ticket.save()
            return Response({'message': f'Soát vé thành công cho ghế {ticket.seat.row}{ticket.seat.number}!'}, status=status.HTTP_200_OK)
        except Ticket.DoesNotExist:
            return Response({'error': 'Mã vé QR không hợp lệ hoặc không tồn tại.'}, status=status.HTTP_404_NOT_FOUND)

class PayOSWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        payload = request.data

        if not getattr(settings, 'PAYOS_SKIP_SIGNATURE_CHECK', False):
            pass

        data = payload.get('data', {})
        order_id = data.get('orderCode')
        success = payload.get('success', False) or payload.get('code') == '00'

        if not order_id:
            return Response({'error': 'Thiếu orderCode'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                order = Order.objects.select_for_update().get(id=order_id)

                if order.status == OrderStatusEnum.PAID:
                    return Response({'status': 'already_processed'}, status=status.HTTP_200_OK)

                tickets = Ticket.objects.filter(order=order)

                if success:
                    order.status = OrderStatusEnum.PAID
                    order.save()

                    seat_ids = tickets.values_list('seat_id', flat=True)
                    if order.event:
                        order.event.seats.filter(id__in=seat_ids).update(status=SeatStatusEnum.SOLD, locked_until=None)

                    transaction.on_commit(lambda: send_payment_success_email(order))
                else:
                    order.status = OrderStatusEnum.CANCELLED
                    order.save()

                    seat_ids = tickets.values_list('seat_id', flat=True)
                    if order.event:
                        order.event.seats.filter(id__in=seat_ids).update(status=SeatStatusEnum.AVAILABLE, locked_until=None)

            return Response({'status': 'success'}, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({'error': 'Không tìm thấy đơn hàng'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)