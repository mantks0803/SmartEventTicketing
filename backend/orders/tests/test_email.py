from django.core import mail
from django.test import override_settings

from orders.models import OrderStatusEnum
from orders.services import confirm_order_payment, hold_seats
from orders.utils import send_payment_success_email

from .base import OrderTestBase


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    DEFAULT_FROM_EMAIL='SmartTicket <noreply@smartticket.test>',
    FRONTEND_URL='http://localhost:5173',
)
class PaymentSuccessEmailTests(OrderTestBase):
    def create_paid_order(self, seat_ids):
        order = hold_seats(self.customer, seat_ids)
        confirm_order_payment(
            order.id,
            amount=order.total_amount,
            transaction_id=f'EMAIL-{order.id}',
        )
        return order

    def get_html_content(self, email):
        return next(
            alternative.content
            for alternative in email.alternatives
            if alternative.mimetype == 'text/html'
        )

    def test_paid_order_email_contains_ticket_code_and_inline_qr(self):
        order = self.create_paid_order([self.seats[0].id])
        ticket = order.tickets.get()

        result = send_payment_success_email(order.id)

        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]
        html_content = self.get_html_content(email)
        image_attachments = [
            attachment
            for attachment in email.attachments
            if attachment.get_content_type() == 'image/png'
        ]

        self.assertIn(ticket.qr_code, email.body)
        self.assertIn(ticket.qr_code, html_content)
        self.assertIn(f'cid:ticket-qr-{ticket.id}', html_content)
        self.assertEqual(len(image_attachments), 1)
        self.assertEqual(
            image_attachments[0]['Content-ID'],
            f'<ticket-qr-{ticket.id}>',
        )

    def test_each_ticket_has_its_own_code_and_qr_image(self):
        order = self.create_paid_order([
            self.seats[0].id,
            self.seats[1].id,
        ])
        tickets = list(order.tickets.order_by('id'))

        send_payment_success_email(order.id)

        email = mail.outbox[0]
        html_content = self.get_html_content(email)
        image_attachments = [
            attachment
            for attachment in email.attachments
            if attachment.get_content_type() == 'image/png'
        ]

        self.assertEqual(len(image_attachments), 2)
        for ticket in tickets:
            self.assertIn(ticket.qr_code, email.body)
            self.assertIn(ticket.qr_code, html_content)
            self.assertIn(f'cid:ticket-qr-{ticket.id}', html_content)

    def test_pending_order_does_not_send_email(self):
        order = hold_seats(self.customer, [self.seats[0].id])

        result = send_payment_success_email(order.id)

        self.assertFalse(result)
        self.assertEqual(len(mail.outbox), 0)

    def test_paid_order_without_ticket_does_not_send_email(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        order.status = OrderStatusEnum.PAID
        order.save(update_fields=['status', 'updated_at'])

        result = send_payment_success_email(order.id)

        self.assertFalse(result)
        self.assertEqual(len(mail.outbox), 0)
