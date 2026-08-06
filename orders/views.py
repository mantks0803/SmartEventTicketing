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
from authentication.permissions import IsCustomerPermission, IsOrganizerPermission
from .utils import send_payment_success_email

try:
    from payos import PayOS, ItemData, PaymentData
    payos = PayOS(
        client_id=getattr(settings, 'PAYOS_CLIENT_ID', ''),
        api_key=getattr(settings, 'PAYOS_API_KEY', ''),
        checksum_key=getattr(settings, 'PAYOS_CHECKSUM_KEY', '')
    )
except ImportError:
    payos = None


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
        customer = getattr(self.request.user, 'customer', None)
        if not customer:
            return Order.objects.none()
        return Order.objects.filter(customer=customer).order_by('-created_at')


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerPermission]

    def get_queryset(self):
        customer = getattr(self.request.user, 'customer', None)
        if not customer:
            return Order.objects.none()
        return Order.objects.filter(customer=customer)


class CancelOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerPermission]

    def post(self, request, pk):
        customer = getattr(request.user, 'customer', None)
        if not customer:
            return Response({'error': 'Tài khoản không phải là khách hàng.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                order = Order.objects.select_for_update().get(id=pk, customer=customer)
                if order.status != OrderStatusEnum.PENDING:
                    return Response({'error': 'Chỉ có thể hủy đơn hàng đang chờ thanh toán.'}, status=status.HTTP_400_BAD_REQUEST)

                order.status = OrderStatusEnum.CANCELLED
                order.save()

                tickets = Ticket.objects.filter(order=order)
                seat_ids = tickets.values_list('seat_id', flat=True)
                Seat.objects.filter(id__in=seat_ids).update(status=SeatStatusEnum.AVAILABLE, locked_until=None)

            return Response({'message': 'Đã hủy đơn hàng thành công.'}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'error': 'Không tìm thấy đơn hàng hoặc bạn không có quyền hủy đơn này.'}, status=status.HTTP_404_NOT_FOUND)


class CreatePayOSPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerPermission]

    def post(self, request, order_id):
        customer = getattr(request.user, 'customer', None)
        try:
            order = Order.objects.get(id=order_id, customer=customer)
            if order.status != OrderStatusEnum.PENDING:
                return Response({'error': 'Đơn hàng không ở trạng thái chờ thanh toán.'}, status=status.HTTP_400_BAD_REQUEST)

            if getattr(settings, 'PAYOS_SKIP_SIGNATURE_CHECK', False) or not payos:
                checkout_url = f"{settings.FRONTEND_URL}/payment-mock/{order.id}"
            else:
                # Tạo link thanh toán PayOS thật
                domain = settings.FRONTEND_URL
                payment_data = PaymentData(
                    orderCode=order.id,
                    amount=int(order.total_amount),
                    description=f"Thanh toan don #{order.id}"[:25],
                    items=[],
                    cancelUrl=f"{domain}/my-orders",
                    returnUrl=f"{domain}/my-tickets"
                )
                payos_response = payos.createPaymentLink(payment_data)
                checkout_url = payos_response.checkoutUrl

            order.payos_checkout_url = checkout_url
            order.save()

            return Response({'checkoutUrl': checkout_url}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'error': 'Không tìm thấy đơn hàng.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Lỗi cổng thanh toán: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomerTicketListView(generics.ListAPIView):
    serializer_class = CustomerTicketSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerPermission]

    def get_queryset(self):
        customer = getattr(self.request.user, 'customer', None)
        if not customer:
            return Ticket.objects.none()
        return Ticket.objects.filter(order__customer=customer, order__status=OrderStatusEnum.PAID).order_by('-id')


class CheckInView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizerPermission]

    def post(self, request):
        serializer = CheckInInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        qr_code = serializer.validated_data['qr_code']
        organizer = getattr(request.user, 'organizer', None)
        if not organizer:
            return Response({'error': 'Tài khoản không phải Ban tổ chức.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            ticket = Ticket.objects.select_related('seat__event__organizer').get(qr_code=qr_code)
            
            if ticket.seat.event.organizer != organizer:
                return Response({'error': 'Bạn không có quyền soát vé cho sự kiện của Ban tổ chức khác!'}, status=status.HTTP_403_FORBIDDEN)

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

        if not getattr(settings, 'PAYOS_SKIP_SIGNATURE_CHECK', False) and payos:
            try:
                verified_data = payos.verifyPaymentWebhookData(payload)
                data = verified_data.to_dict() if hasattr(verified_data, 'to_dict') else payload.get('data', {})
            except Exception as e:
                return Response({'error': f'Chữ ký Webhook không hợp lệ: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            data = payload.get('data', {})

        order_id = data.get('orderCode')
        success = payload.get('success', False) or payload.get('code') == '00'

        if not order_id:
            return Response({'error': 'Thiếu orderCode trong payload'}, status=status.HTTP_400_BAD_REQUEST)

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