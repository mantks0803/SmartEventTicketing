from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from django.core import mail
from django.test import override_settings
from django.utils import timezone

from events.models import EventStatusEnum
from orders.models import OrderStatusEnum
from orders.services import cancel_pending_order, hold_seats
from seating.models import SeatStatusEnum

from .base import OrderTestBase


class PayOSTests(OrderTestBase):
    @override_settings(
        PAYOS_SKIP_SIGNATURE_CHECK=True,
        FRONTEND_URL='http://localhost:5173',
    )
    def test_customer_can_create_mock_payos_link(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        self.client.force_authenticate(self.customer.user)

        response = self.client.post(
            f'/api/orders/{order.id}/payos-link/',
            {},
            format='json',
        )

        order.refresh_from_db()
        expected_url = (
            f'http://localhost:5173/payment/result?orderId={order.id}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['checkoutUrl'], expected_url)
        self.assertEqual(order.payos_checkout_url, expected_url)

    def test_payos_link_is_blocked_after_event_is_cancelled(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        self.event.status = EventStatusEnum.CANCELLED
        self.event.save(update_fields=['status'])
        self.client.force_authenticate(self.customer.user)

        response = self.client.post(
            f'/api/orders/{order.id}/payos-link/',
            {},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 'event_not_published')

    def test_payos_link_is_blocked_after_event_has_started(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        self.event.start_time = timezone.now() - timedelta(minutes=1)
        self.event.save(update_fields=['start_time'])
        self.client.force_authenticate(self.customer.user)

        response = self.client.post(
            f'/api/orders/{order.id}/payos-link/',
            {},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 'event_already_started')

    @override_settings(PAYOS_SKIP_SIGNATURE_CHECK=False)
    def test_invalid_webhook_signature_is_rejected(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        payload = {
            'success': True,
            'code': '00',
            'data': {
                'orderCode': order.id,
                'amount': 100000,
                'reference': 'PAYOS-INVALID-SIGNATURE',
            },
        }

        with patch('orders.views.payos') as payos_mock:
            payos_mock.verifyPaymentWebhookData.side_effect = ValueError(
                'Invalid signature'
            )
            response = self.client.post(
                '/api/orders/webhook/payos/',
                payload,
                format='json',
            )

        order.refresh_from_db()
        self.seats[0].refresh_from_db()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(order.status, OrderStatusEnum.PENDING)
        self.assertEqual(self.seats[0].status, SeatStatusEnum.LOCKED)
        self.assertEqual(order.tickets.count(), 0)
        self.assertEqual(order.payments.count(), 0)

    @override_settings(
        PAYOS_SKIP_SIGNATURE_CHECK=True,
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='SmartTicket <noreply@smartticket.test>',
    )
    def test_webhook_is_idempotent(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        payload = {
            'success': True,
            'code': '00',
            'data': {
                'orderCode': order.id,
                'amount': 100000,
                'reference': 'PAYOS-WEBHOOK-001',
            },
        }

        # Act: PayOS gửi lại cùng một webhook hai lần.
        with self.captureOnCommitCallbacks(execute=True):
            first_response = self.client.post(
                '/api/orders/webhook/payos/',
                payload,
                format='json',
            )
        with self.captureOnCommitCallbacks(execute=True):
            second_response = self.client.post(
                '/api/orders/webhook/payos/',
                payload,
                format='json',
            )

        # Assert: dữ liệu thanh toán, vé và email không bị tạo lặp.
        order.refresh_from_db()
        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(first_response.data['status'], 'success')
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(second_response.data['status'], 'already_processed')
        self.assertEqual(order.status, OrderStatusEnum.PAID)
        self.assertEqual(order.tickets.count(), 1)
        self.assertEqual(order.payments.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['customer@example.com'])
        self.assertIn(f'#{order.id}', mail.outbox[0].subject)

    @override_settings(PAYOS_SKIP_SIGNATURE_CHECK=True)
    def test_success_webhook_cannot_revive_cancelled_order(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        cancel_pending_order(order.id, customer=self.customer)

        response = self.client.post(
            '/api/orders/webhook/payos/',
            {
                'success': True,
                'code': '00',
                'data': {
                    'orderCode': order.id,
                    'amount': 100000,
                    'reference': 'PAYOS-WEBHOOK-002',
                },
            },
            format='json',
        )

        order.refresh_from_db()
        self.seats[0].refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ignored')
        self.assertEqual(order.status, OrderStatusEnum.CANCELLED)
        self.assertEqual(self.seats[0].status, SeatStatusEnum.AVAILABLE)
        self.assertEqual(order.tickets.count(), 0)

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='SmartTicket <noreply@smartticket.test>',
    )
    def test_customer_can_reconcile_paid_order_directly_with_payos(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        payment_info = SimpleNamespace(
            status='PAID',
            orderCode=order.id,
            amount=100000,
            amountPaid=100000,
            amountRemaining=0,
            id='payment-link-001',
            transactions=[SimpleNamespace(reference='PAYOS-RECONCILE-001')],
        )
        self.client.force_authenticate(self.customer.user)

        with patch('orders.views.payos') as payos_mock:
            payos_mock.getPaymentLinkInformation.return_value = payment_info
            with self.captureOnCommitCallbacks(execute=True):
                response = self.client.post(
                    f'/api/orders/{order.id}/reconcile-payos/',
                    {},
                    format='json',
                )
                second_response = self.client.post(
                    f'/api/orders/{order.id}/reconcile-payos/',
                    {},
                    format='json',
                )

        order.refresh_from_db()
        self.seats[0].refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['payos_status'], 'PAID')
        self.assertEqual(response.data['order']['status'], OrderStatusEnum.PAID)
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(order.status, OrderStatusEnum.PAID)
        self.assertEqual(self.seats[0].status, SeatStatusEnum.SOLD)
        self.assertEqual(order.tickets.count(), 1)
        self.assertEqual(order.payments.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_pending_payos_reconciliation_does_not_issue_ticket(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        payment_info = SimpleNamespace(status='PENDING')
        self.client.force_authenticate(self.customer.user)

        with patch('orders.views.payos') as payos_mock:
            payos_mock.getPaymentLinkInformation.return_value = payment_info
            response = self.client.post(
                f'/api/orders/{order.id}/reconcile-payos/',
                {},
                format='json',
            )

        order.refresh_from_db()
        self.seats[0].refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'waiting')
        self.assertEqual(response.data['payos_status'], 'PENDING')
        self.assertEqual(order.status, OrderStatusEnum.PENDING)
        self.assertEqual(self.seats[0].status, SeatStatusEnum.LOCKED)
        self.assertEqual(order.tickets.count(), 0)
        self.assertEqual(order.payments.count(), 0)

    def test_reconciliation_rejects_mismatched_payos_order_data(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        payment_info = SimpleNamespace(
            status='PAID',
            orderCode=order.id + 999,
            amount=100000,
            amountPaid=100000,
            amountRemaining=0,
            transactions=[SimpleNamespace(reference='PAYOS-WRONG-ORDER')],
        )
        self.client.force_authenticate(self.customer.user)

        with patch('orders.views.payos') as payos_mock:
            payos_mock.getPaymentLinkInformation.return_value = payment_info
            response = self.client.post(
                f'/api/orders/{order.id}/reconcile-payos/',
                {},
                format='json',
            )

        order.refresh_from_db()
        self.seats[0].refresh_from_db()
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data['code'], 'payos_data_mismatch')
        self.assertEqual(order.status, OrderStatusEnum.PENDING)
        self.assertEqual(self.seats[0].status, SeatStatusEnum.LOCKED)
        self.assertEqual(order.tickets.count(), 0)
        self.assertEqual(order.payments.count(), 0)

    def test_customer_cannot_reconcile_another_customers_order(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        other_customer = self.create_customer(3)
        self.client.force_authenticate(other_customer.user)

        with patch('orders.views.payos') as payos_mock:
            response = self.client.post(
                f'/api/orders/{order.id}/reconcile-payos/',
                {},
                format='json',
            )

        order.refresh_from_db()
        self.assertEqual(response.status_code, 404)
        payos_mock.getPaymentLinkInformation.assert_not_called()
        self.assertEqual(order.status, OrderStatusEnum.PENDING)
        self.assertEqual(order.tickets.count(), 0)
