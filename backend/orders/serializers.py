from django.utils import timezone
from rest_framework import serializers

from events.models import EventCategoryEnum, EventStatusEnum
from orders.models import (
    Order,
    OrderItem,
    OrderStatusEnum,
    Payment,
    PaymentStatusEnum,
    Ticket,
)
from orders.services import MAX_SEATS_PER_ORDER
from seating.serializers import SeatSerializer


class TicketSerializer(serializers.ModelSerializer):
    seat_details = SeatSerializer(source='seat', read_only=True)
    ticket_type_name = serializers.CharField(
        source='ticket_type.name',
        read_only=True,
    )

    class Meta:
        model = Ticket
        fields = [
            'id', 'seat', 'seat_details', 'ticket_type_name',
            'qr_code', 'is_checked_in', 'issued_at', 'checked_in_at',
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    seat_details = SeatSerializer(source='seat', read_only=True)
    ticket_type_name = serializers.CharField(
        source='ticket_type.name',
        read_only=True,
    )

    class Meta:
        model = OrderItem
        fields = [
            'id', 'seat', 'seat_details', 'ticket_type',
            'ticket_type_name', 'unit_price',
        ]


class CustomerTicketSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    event_id = serializers.IntegerField(source='seat.event.id', read_only=True)
    event_title = serializers.CharField(
        source='seat.event.title',
        read_only=True,
    )
    event_thumbnail = serializers.CharField(
        source='seat.event.thumbnail',
        read_only=True,
    )
    event_location = serializers.CharField(
        source='seat.event.location',
        read_only=True,
    )
    event_start_time = serializers.DateTimeField(
        source='seat.event.start_time',
        read_only=True,
    )
    seat_name = serializers.CharField(source='seat.seat_name', read_only=True)
    seat_row = serializers.CharField(source='seat.row', read_only=True)
    seat_number = serializers.IntegerField(source='seat.number', read_only=True)
    ticket_type_name = serializers.CharField(
        source='ticket_type.name',
        read_only=True,
    )
    price = serializers.SerializerMethodField()

    def get_price(self, ticket):
        for item in ticket.order.items.all():
            if item.seat_id == ticket.seat_id:
                return str(item.unit_price)
        return str(ticket.ticket_type.price)

    class Meta:
        model = Ticket
        fields = [
            'id', 'order_id', 'event_id', 'event_title', 'event_thumbnail',
            'event_location', 'event_start_time', 'seat_name', 'seat_row',
            'seat_number', 'ticket_type_name', 'price', 'qr_code',
            'is_checked_in', 'issued_at', 'checked_in_at',
        ]


class OrderSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)
    event_thumbnail = serializers.CharField(
        source='event.thumbnail',
        read_only=True,
    )
    items = OrderItemSerializer(many=True, read_only=True)
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'event', 'event_title', 'event_thumbnail',
            'total_amount', 'status', 'expires_at', 'created_at',
            'updated_at', 'items', 'tickets',
        ]


class HoldSeatsInputSerializer(serializers.Serializer):
    seat_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        max_length=MAX_SEATS_PER_ORDER,
    )

    def validate_seat_ids(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                'Danh sách ghế không được chứa ID trùng lặp.'
            )
        return value


class CheckInInputSerializer(serializers.Serializer):
    qr_code = serializers.CharField(max_length=250)


class RevenueByTicketTypeSerializer(serializers.Serializer):
    ticket_type_id = serializers.IntegerField()
    ticket_type_name = serializers.CharField()
    sold_quantity = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=16, decimal_places=2)


class RevenueTransactionSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    customer_name = serializers.CharField()
    seat_count = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=16, decimal_places=2)
    created_at = serializers.DateTimeField()


class OrganizerEventRevenueReportSerializer(serializers.Serializer):
    event_id = serializers.IntegerField()
    event_title = serializers.CharField()
    event_status = serializers.CharField()
    is_payout_completed = serializers.BooleanField()
    total_seats = serializers.IntegerField()
    available_seats = serializers.IntegerField()
    locked_seats = serializers.IntegerField()
    sold_seats = serializers.IntegerField()
    checked_in_tickets = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=16, decimal_places=2)
    revenue_by_ticket_type = RevenueByTicketTypeSerializer(many=True)
    transactions = RevenueTransactionSerializer(many=True)


class AdminRevenueReportQuerySerializer(serializers.Serializer):
    event_id = serializers.IntegerField(required=False, min_value=1)
    organizer_id = serializers.IntegerField(required=False, min_value=1)
    category = serializers.ChoiceField(
        required=False,
        choices=EventCategoryEnum.choices,
    )
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)

    def validate(self, data):
        date_from = data.get('date_from')
        date_to = data.get('date_to')

        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError({
                'date_to': 'Ngày kết thúc phải lớn hơn hoặc bằng ngày bắt đầu.'
            })

        return data


class AdminRevenueOverviewSerializer(serializers.Serializer):
    total_revenue = serializers.DecimalField(max_digits=16, decimal_places=2)
    total_paid_orders = serializers.IntegerField()
    total_tickets_sold = serializers.IntegerField()
    total_events = serializers.IntegerField()
    total_checked_in = serializers.IntegerField()


class RevenueByMonthSerializer(serializers.Serializer):
    month = serializers.CharField()
    total_revenue = serializers.DecimalField(max_digits=16, decimal_places=2)


class RevenueByCategorySerializer(serializers.Serializer):
    category = serializers.CharField()
    category_name = serializers.CharField()
    total_revenue = serializers.DecimalField(max_digits=16, decimal_places=2)


class RevenueByOrganizerSerializer(serializers.Serializer):
    organizer_id = serializers.IntegerField()
    company_name = serializers.CharField()
    total_revenue = serializers.DecimalField(max_digits=16, decimal_places=2)


class RevenueByEventSerializer(serializers.Serializer):
    event_id = serializers.IntegerField()
    title = serializers.CharField()
    total_revenue = serializers.DecimalField(max_digits=16, decimal_places=2)


class AdminRevenueReportSerializer(serializers.Serializer):
    overview = AdminRevenueOverviewSerializer()
    revenue_by_month = RevenueByMonthSerializer(many=True)
    revenue_by_category = RevenueByCategorySerializer(many=True)
    revenue_by_organizer = RevenueByOrganizerSerializer(many=True)
    revenue_by_event = RevenueByEventSerializer(many=True)


class RevenueFilterEventSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()


class RevenueFilterOrganizerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    company_name = serializers.CharField()


class RevenueFilterCategorySerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class AdminRevenueFilterSerializer(serializers.Serializer):
    events = RevenueFilterEventSerializer(many=True)
    organizers = RevenueFilterOrganizerSerializer(many=True)
    categories = RevenueFilterCategorySerializer(many=True)


class AdminPaymentQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(
        required=False,
        choices=OrderStatusEnum.choices,
    )
    event_id = serializers.IntegerField(required=False, min_value=1)
    organizer_id = serializers.IntegerField(required=False, min_value=1)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    page = serializers.IntegerField(required=False, min_value=1)
    page_size = serializers.IntegerField(required=False, min_value=1, max_value=100)

    def validate(self, data):
        date_from = data.get('date_from')
        date_to = data.get('date_to')

        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError({
                'date_to': 'Ngày kết thúc phải lớn hơn hoặc bằng ngày bắt đầu.'
            })

        return data


def get_admin_payment_warning(order):
    """Tính cảnh báo từ dữ liệu hiện có, không lưu thêm field vào DB."""
    item_count = getattr(order, 'item_count', None)
    if item_count is None:
        item_count = order.items.count()

    ticket_count = getattr(order, 'ticket_count', None)
    if ticket_count is None:
        ticket_count = order.tickets.count()

    success_count = getattr(order, 'successful_payment_count', None)
    if success_count is None:
        success_count = order.payments.filter(
            status=PaymentStatusEnum.SUCCESS,
        ).count()
    invalid_amount_count = getattr(order, 'invalid_amount_payment_count', 0)
    missing_reference_count = getattr(order, 'missing_reference_payment_count', 0)
    foreign_ticket_count = getattr(order, 'foreign_ticket_count', 0)

    if foreign_ticket_count:
        return {
            'needs_attention': True,
            'warning_code': 'SEAT_ASSIGNED_TO_ANOTHER_ORDER',
            'warning_message': 'Một ghế trong đơn đã có vé thuộc đơn hàng khác.',
        }

    if order.status != OrderStatusEnum.PAID and success_count:
        return {
            'needs_attention': True,
            'warning_code': 'PAYMENT_SUCCESS_ORDER_NOT_PAID',
            'warning_message': 'Đã có thanh toán thành công nhưng đơn chưa ở trạng thái PAID.',
        }

    if order.status == OrderStatusEnum.PAID and not success_count:
        return {
            'needs_attention': True,
            'warning_code': 'PAID_WITHOUT_PAYMENT',
            'warning_message': 'Đơn đã PAID nhưng chưa có bản ghi thanh toán thành công.',
        }

    if invalid_amount_count:
        return {
            'needs_attention': True,
            'warning_code': 'PAYMENT_AMOUNT_MISMATCH',
            'warning_message': 'Số tiền trong bản ghi thanh toán không khớp đơn hàng.',
        }

    if missing_reference_count:
        return {
            'needs_attention': True,
            'warning_code': 'MISSING_TRANSACTION_REFERENCE',
            'warning_message': 'Thanh toán thành công nhưng chưa có mã giao dịch ngân hàng.',
        }

    if order.status == OrderStatusEnum.PAID and ticket_count != item_count:
        return {
            'needs_attention': True,
            'warning_code': 'PAID_WITHOUT_ENOUGH_TICKETS',
            'warning_message': 'Đơn đã PAID nhưng số vé phát hành chưa khớp số ghế đã mua.',
        }

    return {
        'needs_attention': False,
        'warning_code': '',
        'warning_message': '',
    }


class AdminPaymentListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.user.name', read_only=True)
    customer_email = serializers.CharField(source='customer.user.email', read_only=True)
    event_title = serializers.SerializerMethodField()
    organizer_name = serializers.SerializerMethodField()
    transaction_id = serializers.SerializerMethodField()
    payment_status = serializers.SerializerMethodField()
    item_count = serializers.IntegerField(read_only=True)
    ticket_count = serializers.IntegerField(read_only=True)
    needs_attention = serializers.SerializerMethodField()
    warning_code = serializers.SerializerMethodField()
    warning_message = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'customer_name', 'customer_email', 'event', 'event_title',
            'organizer_name', 'total_amount', 'status', 'transaction_id',
            'payment_status', 'item_count', 'ticket_count', 'created_at',
            'updated_at', 'needs_attention', 'warning_code', 'warning_message',
        ]

    def get_event_title(self, order):
        return order.event.title if order.event else 'Sự kiện không còn tồn tại'

    def get_organizer_name(self, order):
        if not order.event:
            return 'Không xác định'
        return order.event.organizer.company_name

    def _get_main_payment(self, order):
        payments = list(order.payments.all())
        return next(
            (payment for payment in payments if payment.status == PaymentStatusEnum.SUCCESS),
            payments[0] if payments else None,
        )

    def get_transaction_id(self, order):
        payment = self._get_main_payment(order)
        return payment.transaction_id if payment else None

    def get_payment_status(self, order):
        payment = self._get_main_payment(order)
        return payment.status if payment else None

    def get_needs_attention(self, order):
        return get_admin_payment_warning(order)['needs_attention']

    def get_warning_code(self, order):
        return get_admin_payment_warning(order)['warning_code']

    def get_warning_message(self, order):
        return get_admin_payment_warning(order)['warning_message']


class AdminPaymentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'provider', 'transaction_id', 'amount', 'status',
            'created_at', 'updated_at',
        ]


class AdminPaymentDetailSerializer(AdminPaymentListSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    tickets = TicketSerializer(many=True, read_only=True)
    payments = AdminPaymentRecordSerializer(many=True, read_only=True)

    class Meta(AdminPaymentListSerializer.Meta):
        fields = AdminPaymentListSerializer.Meta.fields + [
            'payos_checkout_url', 'expires_at', 'items', 'tickets', 'payments',
        ]


class AdminPaymentSummarySerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    paid_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    cancelled_expired_orders = serializers.IntegerField()
    needs_attention = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=16, decimal_places=2)


class AdminPayoutQuerySerializer(serializers.Serializer):
    """Kiểm tra các bộ lọc ở tab quyết toán cho Ban tổ chức."""

    search = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(
        required=False,
        choices=['PENDING', 'COMPLETED'],
    )
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    page = serializers.IntegerField(required=False, min_value=1)
    page_size = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=100,
    )

    def validate(self, data):
        date_from = data.get('date_from')
        date_to = data.get('date_to')

        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError({
                'date_to': 'Ngày kết thúc phải lớn hơn hoặc bằng ngày bắt đầu.'
            })

        return data


class AdminPayoutEventSerializer(serializers.Serializer):
    """Thông tin gọn của một sự kiện trong danh sách quyết toán."""

    event_id = serializers.IntegerField(source='id', read_only=True)
    event_title = serializers.CharField(source='title', read_only=True)
    event_thumbnail = serializers.CharField(source='thumbnail', read_only=True)
    organizer_id = serializers.IntegerField(read_only=True)
    organizer_name = serializers.CharField(
        source='organizer.company_name',
        read_only=True,
    )
    start_time = serializers.DateTimeField(read_only=True)
    event_status = serializers.CharField(source='status', read_only=True)
    is_payout_completed = serializers.BooleanField(read_only=True)
    paid_orders = serializers.IntegerField(read_only=True)
    sold_tickets = serializers.IntegerField(read_only=True)
    checked_in_tickets = serializers.IntegerField(read_only=True)
    total_revenue = serializers.DecimalField(
        max_digits=16,
        decimal_places=2,
        read_only=True,
    )
    can_settle = serializers.SerializerMethodField()

    def get_can_settle(self, event):
        return bool(
            event.status == EventStatusEnum.PUBLISHED
            and event.start_time <= timezone.now()
            and event.paid_orders > 0
            and not event.is_payout_completed
        )


class AdminPayoutSummarySerializer(serializers.Serializer):
    pending_events = serializers.IntegerField()
    pending_revenue = serializers.DecimalField(
        max_digits=16,
        decimal_places=2,
    )
    completed_events = serializers.IntegerField()
    completed_revenue = serializers.DecimalField(
        max_digits=16,
        decimal_places=2,
    )


class AdminPayoutTransactionSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    customer_name = serializers.CharField()
    customer_email = serializers.EmailField()
    ticket_count = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=16, decimal_places=2)
    created_at = serializers.DateTimeField()


class AdminPayoutEventDetailSerializer(AdminPayoutEventSerializer):
    revenue_by_ticket_type = RevenueByTicketTypeSerializer(
        many=True,
        read_only=True,
    )
    transactions = AdminPayoutTransactionSerializer(
        many=True,
        read_only=True,
    )
