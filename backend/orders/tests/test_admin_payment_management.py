from types import SimpleNamespace
from unittest.mock import patch

from django.core import mail
from django.test import override_settings
from django.utils import timezone

from authentication.models import User
from orders.models import Order, OrderStatusEnum, Payment, PaymentStatusEnum
from orders.services import cancel_pending_order, confirm_order_payment, hold_seats
from seating.models import SeatStatusEnum

from .base import OrderTestBase


class AdminPaymentManagementTests(OrderTestBase):
    def setUp(self):
        super().setUp()
        self.admin = User.objects.create_user(
            username='payment-admin',
            email='payment-admin@example.com',
            phone_number='0903999999',
            name='Payment Admin',
            type='ADMIN',
            password='123456',
        )

    def test_admin_can_list_filter_view_detail_and_summary(self):
        paid_order = hold_seats(self.customer, [self.seats[0].id])
        confirm_order_payment(
            paid_order.id,
            amount=paid_order.total_amount,
            transaction_id='ADMIN-PAYMENT-001',
        )
        pending_order = hold_seats(self.customer, [self.seats[1].id])
        cancelled_order = hold_seats(self.customer, [self.seats[2].id])
        cancel_pending_order(cancelled_order.id, customer=self.customer)

        # Dữ liệu cũ bất thường: Order PAID nhưng không có Payment.
        unusual_order = Order.objects.create(
            customer=self.customer,
            event=self.event,
            total_amount=100000,
            status=OrderStatusEnum.PAID,
        )
        self.client.force_authenticate(self.admin)

        list_response = self.client.get(
            '/api/orders/admin/payments/?page=1&page_size=10'
        )
        search_response = self.client.get(
            '/api/orders/admin/payments/?search=ADMIN-PAYMENT-001'
        )
        filter_response = self.client.get(
            f'/api/orders/admin/payments/?status=PENDING&event_id={self.event.id}'
        )
        detail_response = self.client.get(
            f'/api/orders/admin/payments/{paid_order.id}/'
        )
        unusual_response = self.client.get(
            f'/api/orders/admin/payments/{unusual_order.id}/'
        )
        summary_response = self.client.get(
            '/api/orders/admin/payments/summary/'
        )

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.data['count'], 4)
        self.assertEqual(search_response.data['count'], 1)
        self.assertEqual(search_response.data['results'][0]['id'], paid_order.id)
        self.assertEqual(filter_response.data['count'], 1)
        self.assertEqual(filter_response.data['results'][0]['id'], pending_order.id)

        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.data['transaction_id'], 'ADMIN-PAYMENT-001')
        self.assertEqual(len(detail_response.data['items']), 1)
        self.assertEqual(len(detail_response.data['tickets']), 1)
        self.assertEqual(len(detail_response.data['payments']), 1)
        self.assertFalse(detail_response.data['needs_attention'])

        self.assertTrue(unusual_response.data['needs_attention'])
        self.assertEqual(
            unusual_response.data['warning_code'],
            'PAID_WITHOUT_PAYMENT',
        )

        self.assertEqual(summary_response.status_code, 200)
        self.assertEqual(summary_response.data['total_orders'], 4)
        self.assertEqual(summary_response.data['paid_orders'], 2)
        self.assertEqual(summary_response.data['pending_orders'], 1)
        self.assertEqual(summary_response.data['cancelled_expired_orders'], 1)
        self.assertEqual(summary_response.data['needs_attention'], 1)
        self.assertEqual(summary_response.data['total_revenue'], '200000.00')

    def test_warning_is_calculated_without_creating_manual_review_field(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        Payment.objects.create(
            order=order,
            provider='PAYOS',
            transaction_id='ADMIN-WARNING-001',
            amount=order.total_amount,
            status=PaymentStatusEnum.SUCCESS,
        )
        self.client.force_authenticate(self.admin)

        response = self.client.get(
            f'/api/orders/admin/payments/{order.id}/'
        )

        order.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['needs_attention'])
        self.assertEqual(
            response.data['warning_code'],
            'PAYMENT_SUCCESS_ORDER_NOT_PAID',
        )
        self.assertEqual(order.status, OrderStatusEnum.PENDING)

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='SmartTicket <noreply@smartticket.test>',
    )
    def test_admin_can_reconcile_any_pending_order_with_payos(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        payment_info = SimpleNamespace(
            status='PAID',
            orderCode=order.id,
            amount=100000,
            amountPaid=100000,
            amountRemaining=0,
            transactions=[SimpleNamespace(reference='ADMIN-RECONCILE-001')],
        )
        self.client.force_authenticate(self.admin)

        with patch('orders.views.payos') as payos_mock:
            payos_mock.getPaymentLinkInformation.return_value = payment_info
            with self.captureOnCommitCallbacks(execute=True):
                response = self.client.post(
                    f'/api/orders/admin/payments/{order.id}/reconcile-payos/',
                    {},
                    format='json',
                )

        order.refresh_from_db()
        self.seats[0].refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['payos_status'], 'PAID')
        self.assertEqual(order.status, OrderStatusEnum.PAID)
        self.assertEqual(self.seats[0].status, SeatStatusEnum.SOLD)
        self.assertEqual(order.tickets.count(), 1)
        self.assertEqual(order.payments.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_admin_reconcile_keeps_pending_order_when_payos_is_pending(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        self.client.force_authenticate(self.admin)

        with patch('orders.views.payos') as payos_mock:
            payos_mock.getPaymentLinkInformation.return_value = SimpleNamespace(
                status='PENDING'
            )
            response = self.client.post(
                f'/api/orders/admin/payments/{order.id}/reconcile-payos/',
                {},
                format='json',
            )

        order.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'waiting')
        self.assertEqual(order.status, OrderStatusEnum.PENDING)
        self.assertEqual(order.tickets.count(), 0)

    def test_non_admin_is_blocked_and_invalid_filters_return_400(self):
        order = hold_seats(self.customer, [self.seats[0].id])

        anonymous_response = self.client.get('/api/orders/admin/payments/')
        self.client.force_authenticate(self.customer.user)
        customer_response = self.client.get('/api/orders/admin/payments/')
        reconcile_response = self.client.post(
            f'/api/orders/admin/payments/{order.id}/reconcile-payos/',
            {},
            format='json',
        )

        self.client.force_authenticate(self.admin)
        invalid_status = self.client.get(
            '/api/orders/admin/payments/?status=INVALID'
        )
        invalid_dates = self.client.get(
            '/api/orders/admin/payments/?date_from=2026-08-10&date_to=2026-08-01'
        )
        invalid_page_size = self.client.get(
            '/api/orders/admin/payments/?page_size=101'
        )

        self.assertEqual(anonymous_response.status_code, 401)
        self.assertEqual(customer_response.status_code, 403)
        self.assertEqual(reconcile_response.status_code, 403)
        self.assertEqual(invalid_status.status_code, 400)
        self.assertEqual(invalid_dates.status_code, 400)
        self.assertEqual(invalid_page_size.status_code, 400)
