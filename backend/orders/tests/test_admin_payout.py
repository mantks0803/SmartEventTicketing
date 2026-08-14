from datetime import timedelta

from django.utils import timezone

from authentication.models import User
from events.models import EventStatusEnum
from orders.models import OrderStatusEnum
from orders.services import cancel_pending_order, confirm_order_payment, hold_seats

from .base import OrderTestBase


class AdminPayoutTests(OrderTestBase):
    def setUp(self):
        super().setUp()
        self.admin = User.objects.create_user(
            username='payout-admin',
            email='payout-admin@example.com',
            phone_number='0903888888',
            name='Payout Admin',
            type='ADMIN',
            password='123456',
        )

    def create_paid_order(self, seat, transaction_id):
        order = hold_seats(self.customer, [seat.id])
        confirm_order_payment(
            order.id,
            amount=order.total_amount,
            transaction_id=transaction_id,
        )
        order.refresh_from_db()
        return order

    def move_event_to_past(self, event):
        event.start_time = timezone.now() - timedelta(days=2)
        event.save(update_fields=['start_time'])

    def test_admin_can_view_payout_list_summary_and_detail(self):
        # Arrange: một sự kiện chờ quyết toán và một sự kiện đã quyết toán.
        first_order = self.create_paid_order(
            self.seats[0],
            'PAYOUT-LIST-001',
        )
        self.create_paid_order(self.seats[1], 'PAYOUT-LIST-002')
        pending_order = hold_seats(self.customer, [self.seats[2].id])
        cancelled_order = hold_seats(self.customer, [self.seats[3].id])
        cancel_pending_order(cancelled_order.id, customer=self.customer)

        checked_ticket = first_order.tickets.get()
        checked_ticket.is_checked_in = True
        checked_ticket.checked_in_at = timezone.now()
        checked_ticket.save(update_fields=['is_checked_in', 'checked_in_at'])
        self.move_event_to_past(self.event)

        self.create_paid_order(self.other_seat, 'PAYOUT-LIST-003')
        self.other_event.is_payout_completed = True
        self.other_event.save(update_fields=['is_payout_completed'])
        self.move_event_to_past(self.other_event)

        self.client.force_authenticate(self.admin)

        # Act: tải danh sách, card tổng quan, bộ lọc và chi tiết.
        list_response = self.client.get('/api/orders/admin/payouts/')
        summary_response = self.client.get('/api/orders/admin/payouts/summary/')
        pending_response = self.client.get(
            '/api/orders/admin/payouts/?status=PENDING'
        )
        search_response = self.client.get(
            '/api/orders/admin/payouts/?search=Event%201'
        )
        detail_response = self.client.get(
            f'/api/orders/admin/payouts/{self.event.id}/'
        )

        # Assert: chỉ Order PAID được tính vào số đơn và doanh thu.
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.data['count'], 2)
        self.assertEqual(summary_response.data['pending_events'], 1)
        self.assertEqual(summary_response.data['pending_revenue'], '200000.00')
        self.assertEqual(summary_response.data['completed_events'], 1)
        self.assertEqual(summary_response.data['completed_revenue'], '200000.00')
        self.assertEqual(pending_response.data['count'], 1)
        self.assertEqual(search_response.data['count'], 1)

        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.data['paid_orders'], 2)
        self.assertEqual(detail_response.data['sold_tickets'], 2)
        self.assertEqual(detail_response.data['checked_in_tickets'], 1)
        self.assertEqual(detail_response.data['total_revenue'], '200000.00')
        self.assertEqual(len(detail_response.data['transactions']), 2)
        self.assertEqual(
            detail_response.data['revenue_by_ticket_type'][0]['sold_quantity'],
            2,
        )
        self.assertEqual(
            detail_response.data['revenue_by_ticket_type'][0]['revenue'],
            '200000.00',
        )
        self.assertEqual(pending_order.status, OrderStatusEnum.PENDING)

    def test_admin_can_complete_payout_only_once(self):
        # Arrange: tạo thanh toán khi sự kiện còn bán, sau đó đưa ngày về quá khứ.
        order = self.create_paid_order(self.seats[0], 'PAYOUT-COMPLETE-001')
        self.move_event_to_past(self.event)
        old_event_status = self.event.status
        old_order_status = order.status
        old_payment_count = order.payments.count()
        old_ticket_count = order.tickets.count()
        self.client.force_authenticate(self.admin)

        # Act: Admin xác nhận lần đầu rồi thử xác nhận lần hai.
        first_response = self.client.post(
            f'/api/orders/admin/payouts/{self.event.id}/complete/',
            {},
            format='json',
        )
        second_response = self.client.post(
            f'/api/orders/admin/payouts/{self.event.id}/complete/',
            {},
            format='json',
        )

        # Assert: chỉ cờ quyết toán thay đổi, dữ liệu thanh toán và vé giữ nguyên.
        self.event.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(first_response.data['status'], 'success')
        self.assertTrue(first_response.data['event']['is_payout_completed'])
        self.assertEqual(second_response.status_code, 409)
        self.assertEqual(
            second_response.data['code'],
            'payout_already_completed',
        )
        self.assertTrue(self.event.is_payout_completed)
        self.assertEqual(self.event.status, old_event_status)
        self.assertEqual(order.status, old_order_status)
        self.assertEqual(order.payments.count(), old_payment_count)
        self.assertEqual(order.tickets.count(), old_ticket_count)

    def test_invalid_events_cannot_be_completed(self):
        # Arrange: sự kiện tương lai có tiền, sự kiện quá khứ không có tiền.
        self.create_paid_order(self.seats[0], 'PAYOUT-INVALID-001')
        self.move_event_to_past(self.other_event)
        self.client.force_authenticate(self.admin)

        # Act.
        future_response = self.client.post(
            f'/api/orders/admin/payouts/{self.event.id}/complete/',
            {},
            format='json',
        )
        no_revenue_response = self.client.post(
            f'/api/orders/admin/payouts/{self.other_event.id}/complete/',
            {},
            format='json',
        )

        self.event.status = EventStatusEnum.CANCELLED
        self.event.start_time = timezone.now() - timedelta(days=2)
        self.event.save(update_fields=['status', 'start_time'])
        cancelled_response = self.client.post(
            f'/api/orders/admin/payouts/{self.event.id}/complete/',
            {},
            format='json',
        )

        # Assert.
        self.assertEqual(future_response.status_code, 409)
        self.assertEqual(future_response.data['code'], 'event_not_started')
        self.assertEqual(no_revenue_response.status_code, 409)
        self.assertEqual(no_revenue_response.data['code'], 'no_paid_orders')
        self.assertEqual(cancelled_response.status_code, 409)
        self.assertEqual(cancelled_response.data['code'], 'event_not_published')

    def test_only_admin_can_use_payout_api_and_filters_are_validated(self):
        self.create_paid_order(self.seats[0], 'PAYOUT-PERMISSION-001')
        self.move_event_to_past(self.event)

        anonymous_response = self.client.get('/api/orders/admin/payouts/')
        self.client.force_authenticate(self.customer.user)
        customer_response = self.client.get('/api/orders/admin/payouts/')
        complete_response = self.client.post(
            f'/api/orders/admin/payouts/{self.event.id}/complete/',
            {},
            format='json',
        )

        self.client.force_authenticate(self.admin)
        invalid_status = self.client.get(
            '/api/orders/admin/payouts/?status=INVALID'
        )
        invalid_dates = self.client.get(
            '/api/orders/admin/payouts/?date_from=2026-08-10&date_to=2026-08-01'
        )
        missing_detail = self.client.get('/api/orders/admin/payouts/999999/')

        self.assertEqual(anonymous_response.status_code, 401)
        self.assertEqual(customer_response.status_code, 403)
        self.assertEqual(complete_response.status_code, 403)
        self.assertEqual(invalid_status.status_code, 400)
        self.assertEqual(invalid_dates.status_code, 400)
        self.assertEqual(missing_detail.status_code, 404)
