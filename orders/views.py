import uuid
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from payos import PayOS
from payos.type import ItemData, PaymentData

from common.permissions import IsCustomerPermission
from seating.models import Seat
from orders.models import Order, Ticket
from orders.serializers import OrderSerializer, HoldSeatsInputSerializer

payos = PayOS(
    client_id=settings.PAYOS_CLIENT_ID,
    api_key=settings.PAYOS_API_KEY,
    checksum_key=settings.PAYOS_CHECKSUM_KEY
)

class HoldSeatsView(APIView):
    permission_classes = [IsCustomerPermission]

    @transaction.atomic
    def post(self, request):
        serializer = HoldSeatsInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        seat_ids = serializer.validated_data['seat_ids']

        expiration_cutoff = timezone.now() - timedelta(minutes=10)
        expired_seats = Seat.objects.filter(
            id__in=seat_ids,
            status='LOCKED',
            updated_at__lt=expiration_cutoff
        )
        for expired_seat in expired_seats:
            expired_seat.status = 'AVAILABLE'
            expired_seat.save()
            Ticket.objects.filter(seat=expired_seat, order__status='PENDING').update(
                order__status='CANCELLED'
            )

        seats = list(Seat.objects.select_for_update().filter(id__in=seat_ids))

        if len(seats) != len(seat_ids):
            return Response(
                {"detail": "Một hoặc nhiều ghế không tồn tại."},
                status=status.HTTP_400_BAD_REQUEST
            )

        event_ids = {seat.event_id for seat in seats}
        if len(event_ids) > 1:
            return Response(
                {"detail": "Tất cả các ghế phải thuộc cùng một sự kiện."},
                status=status.HTTP_400_BAD_REQUEST
            )

        unavailable_seats = [f"{s.row}{s.number}" for s in seats if s.status != 'AVAILABLE']
        if unavailable_seats:
            return Response(
                {"detail": f"Các ghế sau không còn khả dụng: {', '.join(unavailable_seats)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        total_amount = sum(s.ticket_type.price for s in seats)

        customer = request.user.customer
        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount,
            status='PENDING'
        )

        tickets = []
        for seat in seats:
            seat.status = 'LOCKED'
            seat.save()
            ticket = Ticket.objects.create(
                order=order,
                seat=seat,
                ticket_type=seat.ticket_type,
                qr_code=str(uuid.uuid4())
            )
            tickets.append(ticket)

        order_serializer = OrderSerializer(order)
        return Response(
            {
                "message": "Giữ ghế thành công! Vui lòng thanh toán trong 10 phút.",
                "expires_in_seconds": 600,
                "order": order_serializer.data
            },
            status=status.HTTP_201_CREATED
        )

class CustomerOrderListView(generics.ListAPIView):
    permission_classes = [IsCustomerPermission]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user.customer).order_by('-created_at')

class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsCustomerPermission]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user.customer)

class CancelOrderView(APIView):
    permission_classes = [IsCustomerPermission]

    @transaction.atomic
    def post(self, request, pk):
        try:
            order = Order.objects.select_for_update().get(pk=pk, customer=request.user.customer)
        except Order.DoesNotExist:
            return Response({"detail": "Đơn hàng không tồn tại."}, status=status.HTTP_404_NOT_FOUND)

        if order.status != 'PENDING':
            return Response({"detail": "Chỉ có thể hủy đơn hàng ở trạng thái PENDING."}, status=status.HTTP_400_BAD_REQUEST)

        order.status = 'CANCELLED'
        order.save()

        tickets = Ticket.objects.filter(order=order)
        for ticket in tickets:
            seat = ticket.seat
            if seat.status == 'LOCKED':
                seat.status = 'AVAILABLE'
                seat.save()

        return Response({"message": "Hủy đơn hàng và nhả ghế thành công."}, status=status.HTTP_200_OK)

class CreatePayOSPaymentView(APIView):
    permission_classes = [IsCustomerPermission]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(pk=order_id, customer=request.user.customer)
        except Order.DoesNotExist:
            return Response({"detail": "Đơn hàng không tồn tại."}, status=status.HTTP_404_NOT_FOUND)

        if order.status != 'PENDING':
            return Response({"detail": "Đơn hàng không ở trạng thái chờ thanh toán."}, status=status.HTTP_400_BAD_REQUEST)

        cutoff_time = timezone.now() - timedelta(minutes=10)
        if order.created_at < cutoff_time:
            order.status = 'CANCELLED'
            order.save()
            for ticket in order.tickets.all():
                ticket.seat.status = 'AVAILABLE'
                ticket.seat.save()
            return Response({"detail": "Đơn hàng đã hết hạn giữ chỗ (10 phút). Vui lòng đặt lại ghế."}, status=status.HTTP_400_BAD_REQUEST)

        items = []
        for ticket in order.tickets.all():
            items.append(
                ItemData(
                    name=f"Ve {ticket.seat.row}{ticket.seat.number}",
                    quantity=1,
                    price=int(ticket.ticket_type.price)
                )
            )

        payment_data = PaymentData(
            orderCode=order.id,
            amount=int(order.total_amount),
            description=f"Thanh toan don #{order.id}"[:25],
            items=items,
            cancelUrl="http://localhost:5173/payment/cancel",
            returnUrl="http://localhost:5173/payment/success"
        )

        try:
            payos_response = payos.createPaymentLink(payment_data)
            return Response(
                {
                    "checkout_url": payos_response.checkoutUrl,
                    "qr_code": payos_response.qrCode,
                    "order_id": order.id
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"detail": f"Lỗi tạo link PayOS: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PayOSWebhookView(APIView):
    permission_classes = [permissions.AllowAny]


    #Need to add PostMan testing with PayOS signature in the header for webhook testing :D 
    
    @transaction.atomic
    def post(self, request):
        webhook_body = request.data

        try:
            verified_data = payos.verifyPaymentWebhookData(webhook_body)
            
            if verified_data.code == '00':
                order_id = verified_data.orderCode
                
                try:
                    order = Order.objects.select_for_update().get(pk=order_id)
                except Order.DoesNotExist:
                    return Response({"detail": "Order không tồn tại"}, status=status.HTTP_404_NOT_FOUND)

                if order.status == 'PENDING':
                    order.status = 'PAID'
                    order.save()

                    for ticket in order.tickets.all():
                        seat = ticket.seat
                        seat.status = 'SOLD'
                        seat.save()

            return Response({"status": "success"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)