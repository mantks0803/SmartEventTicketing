import logging
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import Organizer
from authentication.permissions import (
    IsAdminPermission,
    IsCustomerPermission,
    IsOrganizerPermission,
)
from events.models import Event, EventCategoryEnum, EventStatusEnum
from orders.models import (
    Order,
    OrderStatusEnum,
    Payment,
    PaymentStatusEnum,
    Ticket,
)
from orders.serializers import (
    AdminRevenueFilterSerializer,
    AdminRevenueReportQuerySerializer,
    AdminRevenueReportSerializer,
    CheckInInputSerializer,
    CustomerTicketSerializer,
    HoldSeatsInputSerializer,
    OrderSerializer,
    OrganizerEventRevenueReportSerializer,
)
from orders.services import (
    OrderLifecycleError,
    cancel_pending_order,
    confirm_order_payment,
    expire_order,
    expire_stale_orders,
    hold_seats,
)
from orders.utils import send_payment_success_email
from seating.models import SeatStatusEnum


logger = logging.getLogger(__name__)


try:
    from payos import PayOS
    from payos.type import PaymentData

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
            order = Order.objects.select_related('event').get(
                id=order_id,
                customer=customer,
            )
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

        if (
            not order.event
            or order.event.status != EventStatusEnum.PUBLISHED
        ):
            return Response(
                {
                    'error': 'Sự kiện không còn được mở bán.',
                    'code': 'event_not_published',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if order.event.start_time <= timezone.now():
            return Response(
                {
                    'error': 'Sự kiện đã bắt đầu, không thể tiếp tục thanh toán.',
                    'code': 'event_already_started',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if getattr(settings, 'PAYOS_SKIP_SIGNATURE_CHECK', False):
                checkout_url = (
                    f'{settings.FRONTEND_URL.rstrip("/")}'
                    f'/payment/result?orderId={order.id}'
                )
            elif not payos:
                return Response(
                    {'error': 'PayOS chưa được cấu hình đầy đủ trên server.'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            else:
                domain = settings.FRONTEND_URL.rstrip('/')
                payment_result_url = (
                    f'{domain}/payment/result?orderId={order.id}'
                )

                payment_data = PaymentData(
                    orderCode=order.id,
                    amount=int(order.total_amount),
                    description=f'Thanh toan don #{order.id}'[:25],
                    items=[],
                    cancelUrl=f'{payment_result_url}&cancelled=true',
                    returnUrl=payment_result_url,
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
            .select_related(
                'order',
                'order__event',
                'seat',
                'seat__event',
                'ticket_type',
            )
            .prefetch_related('order__items')
            .order_by('-issued_at')
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


class OrganizerEventRevenueReportView(APIView):
    """Báo cáo doanh thu của một sự kiện thuộc Ban tổ chức."""

    permission_classes = [permissions.IsAuthenticated, IsOrganizerPermission]

    def get(self, request, event_id):
        organizer = getattr(request.user, 'organizer', None)

        # Lọc theo cả event và chủ sở hữu để event của BTC khác trả về 404.
        event = get_object_or_404(
            Event,
            id=event_id,
            organizer=organizer,
        )

        # Đồng bộ các ghế đã hết 10 phút giữ trước khi thống kê.
        expire_stale_orders()

        seat_counts = event.seats.aggregate(
            total_seats=Count('id'),
            available_seats=Count(
                'id',
                filter=Q(status=SeatStatusEnum.AVAILABLE),
            ),
            locked_seats=Count(
                'id',
                filter=Q(status=SeatStatusEnum.LOCKED),
            ),
            sold_seats=Count(
                'id',
                filter=Q(status=SeatStatusEnum.SOLD),
            ),
        )

        # Chỉ đơn PAID mới được tính vào doanh thu.
        paid_orders = Order.objects.filter(
            event=event,
            status=OrderStatusEnum.PAID,
        )
        total_revenue = (
            paid_orders.aggregate(total=Sum('total_amount'))['total']
            or Decimal('0.00')
        )

        checked_in_tickets = Ticket.objects.filter(
            order__event=event,
            order__status=OrderStatusEnum.PAID,
            is_checked_in=True,
        ).count()

        # Dùng unit_price đã lưu lúc mua, không dùng giá vé hiện tại.
        ticket_type_queryset = event.ticket_types.annotate(
            sold_quantity=Count(
                'order_items',
                filter=Q(
                    order_items__order__status=OrderStatusEnum.PAID,
                    order_items__order__event=event,
                ),
            ),
            report_revenue=Sum(
                'order_items__unit_price',
                filter=Q(
                    order_items__order__status=OrderStatusEnum.PAID,
                    order_items__order__event=event,
                ),
            ),
        ).order_by('name')

        revenue_by_ticket_type = [
            {
                'ticket_type_id': ticket_type.id,
                'ticket_type_name': ticket_type.name,
                'sold_quantity': ticket_type.sold_quantity,
                'revenue': ticket_type.report_revenue or Decimal('0.00'),
            }
            for ticket_type in ticket_type_queryset
        ]

        # select_related lấy Customer và User cùng query, tránh N+1.
        transaction_queryset = (
            paid_orders
            .select_related('customer__user')
            .annotate(seat_count=Count('items'))
            .order_by('-created_at')
        )
        transactions = [
            {
                'order_id': order.id,
                'customer_name': order.customer.user.name,
                'seat_count': order.seat_count,
                'total_amount': order.total_amount,
                'created_at': order.created_at,
            }
            for order in transaction_queryset
        ]

        report_data = {
            'event_id': event.id,
            'event_title': event.title,
            'event_status': event.status,
            'is_payout_completed': event.is_payout_completed,
            **seat_counts,
            'checked_in_tickets': checked_in_tickets,
            'total_revenue': total_revenue,
            'revenue_by_ticket_type': revenue_by_ticket_type,
            'transactions': transactions,
        }

        serializer = OrganizerEventRevenueReportSerializer(report_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminRevenueReportView(APIView):
    """Báo cáo doanh thu của toàn hệ thống dành cho Admin."""

    permission_classes = [permissions.IsAuthenticated, IsAdminPermission]

    def get(self, request):
        query_serializer = AdminRevenueReportQuerySerializer(
            data=request.query_params,
        )
        query_serializer.is_valid(raise_exception=True)
        filters = query_serializer.validated_data

        # Tạo một queryset gốc để tất cả số liệu dùng chung điều kiện lọc.
        paid_orders = Order.objects.filter(
            status=OrderStatusEnum.PAID,
            event__isnull=False,
        )

        if filters.get('event_id'):
            paid_orders = paid_orders.filter(event_id=filters['event_id'])

        if filters.get('organizer_id'):
            paid_orders = paid_orders.filter(
                event__organizer_id=filters['organizer_id'],
            )

        if filters.get('category'):
            paid_orders = paid_orders.filter(
                event__category=filters['category'],
            )

        if filters.get('date_from'):
            paid_orders = paid_orders.filter(
                created_at__date__gte=filters['date_from'],
            )

        if filters.get('date_to'):
            paid_orders = paid_orders.filter(
                created_at__date__lte=filters['date_to'],
            )

        overview_result = paid_orders.aggregate(
            total_revenue=Sum('total_amount'),
            total_paid_orders=Count('id'),
            total_events=Count('event_id', distinct=True),
        )

        # Đếm OrderItem và Ticket ở query riêng để không nhân đôi tổng doanh thu.
        total_tickets_sold = paid_orders.aggregate(
            total=Count('items'),
        )['total']
        total_checked_in = Ticket.objects.filter(
            order__in=paid_orders,
            is_checked_in=True,
        ).count()

        overview = {
            'total_revenue': (
                overview_result['total_revenue'] or Decimal('0.00')
            ),
            'total_paid_orders': overview_result['total_paid_orders'],
            'total_tickets_sold': total_tickets_sold,
            'total_events': overview_result['total_events'],
            'total_checked_in': total_checked_in,
        }

        # Group theo tháng tạo đơn để frontend hiển thị biểu đồ thời gian.
        month_queryset = (
            paid_orders
            .annotate(report_month=TruncMonth('created_at'))
            .values('report_month')
            .annotate(total_revenue=Sum('total_amount'))
            .order_by('report_month')
        )
        revenue_by_month = [
            {
                'month': row['report_month'].strftime('%Y-%m'),
                'total_revenue': row['total_revenue'],
            }
            for row in month_queryset
        ]

        category_labels = dict(EventCategoryEnum.choices)
        category_queryset = (
            paid_orders
            .values('event__category')
            .annotate(total_revenue=Sum('total_amount'))
            .order_by('event__category')
        )
        revenue_by_category = [
            {
                'category': row['event__category'],
                'category_name': category_labels.get(
                    row['event__category'],
                    row['event__category'],
                ),
                'total_revenue': row['total_revenue'],
            }
            for row in category_queryset
        ]

        organizer_queryset = (
            paid_orders
            .values(
                'event__organizer_id',
                'event__organizer__company_name',
            )
            .annotate(total_revenue=Sum('total_amount'))
            .order_by('-total_revenue', 'event__organizer_id')[:10]
        )
        revenue_by_organizer = [
            {
                'organizer_id': row['event__organizer_id'],
                'company_name': row['event__organizer__company_name'],
                'total_revenue': row['total_revenue'],
            }
            for row in organizer_queryset
        ]

        event_queryset = (
            paid_orders
            .values('event_id', 'event__title')
            .annotate(total_revenue=Sum('total_amount'))
            .order_by('-total_revenue', 'event_id')[:10]
        )
        revenue_by_event = [
            {
                'event_id': row['event_id'],
                'title': row['event__title'],
                'total_revenue': row['total_revenue'],
            }
            for row in event_queryset
        ]

        report_data = {
            'overview': overview,
            'revenue_by_month': revenue_by_month,
            'revenue_by_category': revenue_by_category,
            'revenue_by_organizer': revenue_by_organizer,
            'revenue_by_event': revenue_by_event,
        }

        serializer = AdminRevenueReportSerializer(report_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminRevenueFilterView(APIView):
    """Danh sách giá trị dùng cho các dropdown lọc báo cáo."""

    permission_classes = [permissions.IsAuthenticated, IsAdminPermission]

    def get(self, request):
        events = Event.objects.order_by('title').values('id', 'title')
        organizers = Organizer.objects.order_by('company_name').values(
            'user_id',
            'company_name',
        )

        filter_data = {
            'events': list(events),
            'organizers': [
                {
                    'id': organizer['user_id'],
                    'company_name': organizer['company_name'],
                }
                for organizer in organizers
            ],
            'categories': [
                {'value': value, 'label': label}
                for value, label in EventCategoryEnum.choices
            ],
        }

        serializer = AdminRevenueFilterSerializer(filter_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReconcilePayOSPaymentView(APIView):
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

        if order.status == OrderStatusEnum.PAID:
            return Response({
                'status': 'success',
                'payos_status': 'PAID',
                'order': OrderSerializer(order).data,
            })

        if order.status not in {
            OrderStatusEnum.PENDING,
            OrderStatusEnum.EXPIRED,
        }:
            return Response(
                {
                    'error': (
                        'Đơn hàng đã bị hủy hoặc không còn được phép '
                        'phát hành vé tự động.'
                    ),
                    'code': 'invalid_payment_state',
                },
                status=status.HTTP_409_CONFLICT,
            )

        if not payos:
            return Response(
                {'error': 'PayOS chưa được cấu hình đầy đủ trên server.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            payment_info = payos.getPaymentLinkInformation(order.id)
        except Exception as exc:
            return Response(
                {'error': f'Không thể kiểm tra giao dịch PayOS: {str(exc)}'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        payos_status = str(
            _get_webhook_value(payment_info, 'status') or ''
        ).upper()

        if payos_status != 'PAID':
            return Response({
                'status': 'waiting',
                'payos_status': payos_status or 'UNKNOWN',
                'order': OrderSerializer(order).data,
            })

        payos_order_id = _get_webhook_value(
            payment_info,
            'orderCode',
            'order_code',
        )
        payos_amount = _get_webhook_value(payment_info, 'amount')
        amount_paid = _get_webhook_value(
            payment_info,
            'amountPaid',
            'amount_paid',
        )
        amount_remaining = _get_webhook_value(
            payment_info,
            'amountRemaining',
            'amount_remaining',
        )

        if any(value is None for value in (
            payos_order_id,
            payos_amount,
            amount_paid,
            amount_remaining,
        )):
            return Response(
                {
                    'error': 'Dữ liệu giao dịch PayOS không đầy đủ.',
                    'code': 'invalid_payos_data',
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        try:
            payos_order_id = int(payos_order_id)
            payos_amount = Decimal(str(payos_amount))
            amount_paid = Decimal(str(amount_paid))
            amount_remaining = Decimal(str(amount_remaining))
        except (TypeError, ValueError, InvalidOperation):
            return Response(
                {
                    'error': 'Dữ liệu giao dịch PayOS không hợp lệ.',
                    'code': 'invalid_payos_data',
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if (
            payos_order_id != order.id
            or payos_amount != order.total_amount
            or amount_paid != order.total_amount
            or amount_remaining != Decimal('0')
        ):
            return Response(
                {
                    'error': (
                        'Thông tin mã đơn hoặc số tiền trên PayOS '
                        'không khớp với đơn hàng.'
                    ),
                    'code': 'payos_data_mismatch',
                },
                status=status.HTTP_409_CONFLICT,
            )

        transactions = _get_webhook_value(payment_info, 'transactions') or []
        transaction_id = None

        for payos_transaction in transactions:
            transaction_id = _get_webhook_value(
                payos_transaction,
                'reference',
                'transactionId',
                'transaction_id',
            )
            if transaction_id:
                transaction_id = str(transaction_id).strip()
                break

        if not transaction_id:
            return Response(
                {
                    'error': 'PayOS chưa trả về mã giao dịch ngân hàng.',
                    'code': 'missing_payos_reference',
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        try:
            paid_order, processed = confirm_order_payment(
                order.id,
                amount=amount_paid,
                transaction_id=transaction_id,
                allow_expired=True,
            )
        except OrderLifecycleError as exc:
            return Response(
                {'error': exc.message, 'code': exc.code},
                status=status.HTTP_409_CONFLICT,
            )

        if processed:
            transaction.on_commit(
                lambda paid_order_id=paid_order.id:
                send_payment_success_email(paid_order_id)
            )

        paid_order = (
            Order.objects
            .select_related('event')
            .prefetch_related(
                'items__seat__ticket_type',
                'tickets__seat__ticket_type',
            )
            .get(id=paid_order.id)
        )

        return Response({
            'status': 'success',
            'payos_status': payos_status,
            'order': OrderSerializer(paid_order).data,
        })


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
                {'status': 'ignored_unknown_order'},
                status=status.HTTP_200_OK,
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
                allow_expired=True,
            )
        except OrderLifecycleError as exc:
            if exc.code in {'invalid_payment_state', 'order_expired'}:
                return Response(
                    {'status': 'ignored', 'code': exc.code},
                    status=status.HTTP_200_OK,
                )
            if exc.code == 'seat_unavailable_after_payment':
                logger.error(
                    'PayOS đã báo PAID cho đơn #%s nhưng ghế không còn khả dụng.',
                    order.id,
                )
                return Response(
                    {'status': 'manual_review', 'code': exc.code},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {'error': exc.message, 'code': exc.code},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not processed:
            return Response({'status': 'already_processed'}, status=status.HTTP_200_OK)

        transaction.on_commit(
            lambda order_id=paid_order.id:
            send_payment_success_email(order_id)
        )
        return Response({'status': 'success'}, status=status.HTTP_200_OK)
