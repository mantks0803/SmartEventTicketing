from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.permissions import IsCustomerPermission, IsOrganizerPermission
from orders.models import (
    Order,
    OrderStatusEnum,
    Payment,
    PaymentStatusEnum,
    Ticket,
)
from orders.serializers import (
    CheckInInputSerializer,
    CustomerTicketSerializer,
    HoldSeatsInputSerializer,
    OrderSerializer,
)
from orders.services import (
    OrderLifecycleError,
    cancel_pending_order,
    confirm_order_payment,
    expire_order,
    hold_seats,
)
from orders.utils import send_payment_success_email


try:
    from payos import ItemData, PayOS, PaymentData

    payos_credentials = (
        getattr(settings, 'PAYOS_CLIENT_ID', ''),
        getattr(settings, 'PAYOS_API_KEY', ''),
        getattr(settings, 'PAYOS_CHECKSUM_KEY', ''),
    )
    payos = PayOS(
        client_id=payos_credentials[0],
        api_key=payos_credentials[1],
        checksum_key=payos_credentials[2],
    ) if all(payos_credentials) else None
except ImportError:
    ItemData = None
    PaymentData = None
    payos = None


def _get_webhook_value(data, *keys):
    for key in keys:
        if isinstance(data, dict) and data.get(key) is not None:
            return data.get(key)
        if hasattr(data, key):
            value = getattr(data, key)
            if value is not None:
                return value
    return None


class HoldSeatsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerPermission]

    def post(self, request):
        serializer = HoldSeatsInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        customer = getattr(request.user, 'customer', None)
        if not customer:
            return Response(
                {'error': 'Tài khoản không phải là khách hàng.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            order = hold_seats(customer, serializer.validated_data['seat_ids'])
            order = Order.objects.prefetch_related(
                'items__seat__ticket_type',
                'tickets__seat__ticket_type',
            ).get(id=order.id)
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        except OrderLifecycleError as exc:
            return Response(
                {'error': exc.message, 'code': exc.code},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CustomerOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerPermission]

    def get_queryset(self):
        customer = getattr(self.request.user, 'customer', None)
        if not customer:
            return Order.objects.none()
        return (
            Order.objects.filter(customer=customer)
            .select_related('event')
            .prefetch_related(
                'items__seat__ticket_type',
                'tickets__seat__ticket_type',
            )
            .order_by('-created_at')
        )


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerPermission]

    def get_queryset(self):
        customer = getattr(self.request.user, 'customer', None)
        if not customer:
            return Order.objects.none()
        return (
            Order.objects.filter(customer=customer)
            .select_related('event')
            .prefetch_related(
                'items__seat__ticket_type',
                'tickets__seat__ticket_type',
            )
        )


class CancelOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerPermission]

    def post(self, request, pk):
        customer = getattr(request.user, 'customer', None)
        if not customer:
            return Response(
                {'error': 'Tài khoản không phải là khách hàng.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            order = cancel_pending_order(pk, customer=customer)
        except OrderLifecycleError as exc:
            response_status = (
                status.HTTP_404_NOT_FOUND
                if exc.code == 'order_not_found'
                else status.HTTP_400_BAD_REQUEST
            )
            return Response(
                {'error': exc.message, 'code': exc.code},
                status=response_status,
            )

        if order.status == OrderStatusEnum.EXPIRED:
            return Response(
                {'error': 'Đơn hàng đã hết thời gian giữ ghế.', 'code': 'order_expired'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {'message': 'Đã hủy đơn hàng thành công.'},
            status=status.HTTP_200_OK,
        )


class CreatePayOSPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerPermission]

    def post(self, request, order_id):
        customer = getattr(request.user, 'customer', None)

        try:
            order = Order.objects.get(id=order_id, customer=customer)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Không tìm thấy đơn hàng.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if order.is_expired:
            expire_order(order.id)
            return Response(
                {'error': 'Đơn hàng đã hết thời gian giữ ghế.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if order.status != OrderStatusEnum.PENDING:
            return Response(
                {'error': 'Đơn hàng không ở trạng thái chờ thanh toán.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if getattr(settings, 'PAYOS_SKIP_SIGNATURE_CHECK', False):
                checkout_url = f"{settings.FRONTEND_URL}/payment-mock/{order.id}"
            elif not payos:
                return Response(
                    {'error': 'PayOS chưa được cấu hình đầy đủ trên server.'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            else:
                domain = settings.FRONTEND_URL
                payment_data = PaymentData(
                    orderCode=order.id,
                    amount=int(order.total_amount),
                    description=f"Thanh toan don #{order.id}"[:25],
                    items=[],
                    cancelUrl=f"{domain}/",
                    returnUrl=f"{domain}/my-tickets",
                )
                payos_response = payos.createPaymentLink(payment_data)
                checkout_url = payos_response.checkoutUrl

            order.payos_checkout_url = checkout_url
            order.save(update_fields=['payos_checkout_url', 'updated_at'])
            return Response({'checkoutUrl': checkout_url}, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response(
                {'error': f'Lỗi cổng thanh toán: {str(exc)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CustomerTicketListView(generics.ListAPIView):
    serializer_class = CustomerTicketSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerPermission]

    def get_queryset(self):
        customer = getattr(self.request.user, 'customer', None)
        if not customer:
            return Ticket.objects.none()
        return (
            Ticket.objects.filter(
                order__customer=customer,
                order__status=OrderStatusEnum.PAID,
            )
            .select_related('order', 'seat__event', 'ticket_type')
            .order_by('-id')
        )


class CheckInView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizerPermission]

    def post(self, request):
        serializer = CheckInInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        organizer = getattr(request.user, 'organizer', None)
        if not organizer:
            return Response(
                {'error': 'Tài khoản không phải Ban tổ chức.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            with transaction.atomic():
                ticket = (
                    Ticket.objects.select_for_update()
                    .select_related('order', 'seat__event__organizer')
                    .get(qr_code=serializer.validated_data['qr_code'])
                )

                if ticket.order.status != OrderStatusEnum.PAID:
                    return Response(
                        {'error': 'Vé chưa được thanh toán hoặc không còn hiệu lực.'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if ticket.seat.event.organizer != organizer:
                    return Response(
                        {'error': 'Bạn không có quyền soát vé cho sự kiện của Ban tổ chức khác!'},
                        status=status.HTTP_403_FORBIDDEN,
                    )

                if ticket.is_checked_in:
                    return Response(
                        {'error': 'Vé này đã được soát vé trước đó!'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                ticket.is_checked_in = True
                ticket.checked_in_at = timezone.now()
                ticket.save(update_fields=['is_checked_in', 'checked_in_at'])

            return Response(
                {'message': f'Soát vé thành công cho ghế {ticket.seat.seat_name}!'},
                status=status.HTTP_200_OK,
            )
        except Ticket.DoesNotExist:
            return Response(
                {'error': 'Mã vé QR không hợp lệ hoặc không tồn tại.'},
                status=status.HTTP_404_NOT_FOUND,
            )


class PayOSWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        payload = request.data

        if getattr(settings, 'PAYOS_SKIP_SIGNATURE_CHECK', False):
            verified_data = payload.get('data', {})
        else:
            if not payos:
                return Response(
                    {'error': 'PayOS chưa được cấu hình đầy đủ trên server.'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            try:
                verified_data = payos.verifyPaymentWebhookData(payload)
            except Exception as exc:
                return Response(
                    {'error': f'Chữ ký Webhook không hợp lệ: {str(exc)}'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        order_id = _get_webhook_value(verified_data, 'orderCode', 'order_code')
        amount = _get_webhook_value(verified_data, 'amount')
        transaction_id = _get_webhook_value(
            verified_data,
            'reference',
            'transactionId',
            'transaction_id',
        )
        success = payload.get('success') is True and str(payload.get('code')) == '00'

        if not order_id:
            return Response(
                {'error': 'Thiếu orderCode trong payload.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Không tìm thấy đơn hàng.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not success:
            if order.status != OrderStatusEnum.PENDING:
                return Response(
                    {'status': 'already_processed', 'order_status': order.status},
                    status=status.HTTP_200_OK,
                )

            try:
                cancelled_order = cancel_pending_order(order.id)
            except OrderLifecycleError:
                cancelled_order = order

            payment_amount = order.total_amount
            if amount is not None:
                try:
                    payment_amount = Decimal(str(amount))
                except InvalidOperation:
                    payment_amount = order.total_amount

            payment_defaults = {
                'order': cancelled_order,
                'provider': 'PAYOS',
                'amount': payment_amount,
                'status': PaymentStatusEnum.FAILED,
            }
            if transaction_id:
                Payment.objects.get_or_create(
                    transaction_id=str(transaction_id),
                    defaults=payment_defaults,
                )
            else:
                Payment.objects.create(**payment_defaults)

            return Response({'status': 'payment_failed'}, status=status.HTTP_200_OK)

        if amount is None:
            return Response(
                {'error': 'Thiếu số tiền thanh toán trong webhook.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            paid_order, processed = confirm_order_payment(
                order.id,
                amount=amount,
                transaction_id=transaction_id,
            )
        except OrderLifecycleError as exc:
            if exc.code in {'invalid_payment_state', 'order_expired'}:
                return Response(
                    {'status': 'ignored', 'code': exc.code},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {'error': exc.message, 'code': exc.code},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if paid_order.status == OrderStatusEnum.EXPIRED:
            return Response({'status': 'ignored_expired'}, status=status.HTTP_200_OK)

        if not processed:
            return Response({'status': 'already_processed'}, status=status.HTTP_200_OK)

        transaction.on_commit(lambda: send_payment_success_email(paid_order))
        return Response({'status': 'success'}, status=status.HTTP_200_OK)
