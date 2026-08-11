from decimal import Decimal
from datetime import timedelta

from django.utils import timezone

from events.models import TicketType
from orders.models import OrderStatusEnum
from orders.services import confirm_order_payment, hold_seats
from seating.models import Seat

from .base import OrderTestBase


class OrganizerRevenueReportTests(OrderTestBase):
    def setUp(self):
        super().setUp()

        self.regular_ticket_type = TicketType.objects.create(
            event=self.event,
            name='Phổ thông',
            price=150000,
            quantity=1,
        )
        self.regular_seat = Seat.objects.create(
            event=self.event,
            ticket_type=self.regular_ticket_type,
            row='B',
            number=1,
        )

        # Arrange: tạo một đơn PAID gồm 1 vé VIP và 1 vé phổ thông.
        self.paid_order = hold_seats(
            self.customer,
            [self.seats[0].id, self.regular_seat.id],
        )
        confirm_order_payment(
            self.paid_order.id,
            amount=Decimal('250000.00'),
            transaction_id='REPORT-PAID-001',
        )
        self.paid_order.refresh_from_db()

        checked_in_ticket = self.paid_order.tickets.get(
            seat=self.seats[0],
        )
        checked_in_ticket.is_checked_in = True
        checked_in_ticket.checked_in_at = timezone.now()
        checked_in_ticket.save(
            update_fields=['is_checked_in', 'checked_in_at'],
        )

        # Đơn PENDING này chỉ khóa ghế, không được tính doanh thu.
        pending_customer = self.create_customer(9)
        self.pending_order = hold_seats(
            pending_customer,
            [self.seats[2].id],
        )

        self.report_url = (
            f'/api/orders/organizer/events/{self.event.id}/report/'
        )

    def test_owner_can_view_correct_revenue_report(self):
        self.client.force_authenticate(self.organizer_user)

        # Act: BTC gọi báo cáo của sự kiện do mình sở hữu.
        response = self.client.get(self.report_url)

        # Assert: chỉ đơn PAID được tính vào số vé bán và doanh thu.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['event_id'], self.event.id)
        self.assertEqual(response.data['total_seats'], 7)
        self.assertEqual(response.data['available_seats'], 4)
        self.assertEqual(response.data['locked_seats'], 1)
        self.assertEqual(response.data['sold_seats'], 2)
        self.assertEqual(response.data['checked_in_tickets'], 1)
        self.assertEqual(response.data['total_revenue'], '250000.00')

        revenue_rows = {
            row['ticket_type_name']: row
            for row in response.data['revenue_by_ticket_type']
        }
        self.assertEqual(revenue_rows['VIP']['sold_quantity'], 1)
        self.assertEqual(revenue_rows['VIP']['revenue'], '100000.00')
        self.assertEqual(revenue_rows['Phổ thông']['sold_quantity'], 1)
        self.assertEqual(
            revenue_rows['Phổ thông']['revenue'],
            '150000.00',
        )

        self.assertEqual(len(response.data['transactions']), 1)
        transaction_data = response.data['transactions'][0]
        self.assertEqual(transaction_data['order_id'], self.paid_order.id)
        self.assertEqual(transaction_data['seat_count'], 2)
        self.assertEqual(transaction_data['total_amount'], '250000.00')

    def test_expired_lock_is_released_before_counting_seats(self):
        self.pending_order.expires_at = timezone.now() - timedelta(minutes=1)
        self.pending_order.save(update_fields=['expires_at'])
        self.client.force_authenticate(self.organizer_user)

        response = self.client.get(self.report_url)

        self.pending_order.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['available_seats'], 5)
        self.assertEqual(response.data['locked_seats'], 0)
        self.assertEqual(self.pending_order.status, OrderStatusEnum.EXPIRED)

    def test_other_organizer_receives_not_found(self):
        other_organizer = self.create_organizer(1)
        self.client.force_authenticate(other_organizer.user)

        response = self.client.get(self.report_url)

        # Trả 404 để không làm lộ event của Ban tổ chức khác.
        self.assertEqual(response.status_code, 404)

    def test_customer_cannot_view_report(self):
        self.client.force_authenticate(self.customer.user)

        response = self.client.get(self.report_url)

        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_cannot_view_report(self):
        response = self.client.get(self.report_url)

        self.assertEqual(response.status_code, 401)
