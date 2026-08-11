from orders.models import Ticket
from orders.services import confirm_order_payment, hold_seats

from .base import OrderTestBase


class CheckInTests(OrderTestBase):
    def create_paid_ticket(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        confirm_order_payment(
            order.id,
            amount=100000,
            transaction_id='CHECK-IN-001',
        )
        return order.tickets.get()

    def test_event_organizer_can_check_in_paid_ticket(self):
        ticket = self.create_paid_ticket()
        self.client.force_authenticate(self.organizer_user)

        # Act: BTC của chính sự kiện quét mã QR.
        response = self.client.post(
            '/api/orders/check-in/',
            {'qr_code': ticket.qr_code},
            format='json',
        )

        # Assert: vé được đánh dấu đã dùng và có thời gian check-in.
        ticket.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ticket.is_checked_in)
        self.assertIsNotNone(ticket.checked_in_at)

    def test_ticket_cannot_be_checked_in_twice(self):
        ticket = self.create_paid_ticket()
        self.client.force_authenticate(self.organizer_user)
        self.client.post(
            '/api/orders/check-in/',
            {'qr_code': ticket.qr_code},
            format='json',
        )

        second_response = self.client.post(
            '/api/orders/check-in/',
            {'qr_code': ticket.qr_code},
            format='json',
        )

        self.assertEqual(second_response.status_code, 400)

    def test_other_organizer_cannot_check_in_ticket(self):
        ticket = self.create_paid_ticket()
        other_organizer = self.create_organizer(1)
        self.client.force_authenticate(other_organizer.user)

        response = self.client.post(
            '/api/orders/check-in/',
            {'qr_code': ticket.qr_code},
            format='json',
        )

        ticket.refresh_from_db()
        self.assertEqual(response.status_code, 403)
        self.assertFalse(ticket.is_checked_in)

    def test_customer_cannot_check_in_ticket(self):
        ticket = self.create_paid_ticket()
        self.client.force_authenticate(self.customer.user)

        response = self.client.post(
            '/api/orders/check-in/',
            {'qr_code': ticket.qr_code},
            format='json',
        )

        self.assertEqual(response.status_code, 403)

    def test_invalid_qr_code_returns_not_found(self):
        self.client.force_authenticate(self.organizer_user)

        response = self.client.post(
            '/api/orders/check-in/',
            {'qr_code': 'QR-CODE-DOES-NOT-EXIST'},
            format='json',
        )

        self.assertEqual(response.status_code, 404)

    def test_pending_ticket_cannot_be_checked_in(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        ticket = Ticket.objects.create(
            order=order,
            seat=self.seats[0],
            ticket_type=self.ticket_type,
            qr_code='LEGACY-PENDING-TICKET',
        )
        self.client.force_authenticate(self.organizer_user)

        response = self.client.post(
            '/api/orders/check-in/',
            {'qr_code': ticket.qr_code},
            format='json',
        )

        ticket.refresh_from_db()
        self.assertEqual(response.status_code, 400)
        self.assertFalse(ticket.is_checked_in)
