from orders.models import Ticket
from orders.services import confirm_order_payment, hold_seats

from .base import OrderTestBase


class CustomerTicketTests(OrderTestBase):
    def test_my_tickets_only_returns_paid_tickets_of_current_customer(self):
        # Arrange: tạo một vé đã thanh toán của khách hiện tại.
        own_order = hold_seats(self.customer, [self.seats[0].id])
        confirm_order_payment(
            own_order.id,
            amount=100000,
            transaction_id='TICKET-OWN-001',
        )

        # Tạo một vé đã thanh toán của khách khác.
        other_customer = self.create_customer(4)
        other_order = hold_seats(other_customer, [self.seats[1].id])
        confirm_order_payment(
            other_order.id,
            amount=100000,
            transaction_id='TICKET-OTHER-001',
        )

        # Tạo dữ liệu vé cũ nằm trong đơn PENDING để chắc chắn API không trả về.
        pending_order = hold_seats(self.customer, [self.seats[2].id])
        Ticket.objects.create(
            order=pending_order,
            seat=self.seats[2],
            ticket_type=self.ticket_type,
            qr_code='LEGACY-PENDING-TICKET-LIST',
        )
        self.client.force_authenticate(self.customer.user)

        response = self.client.get('/api/orders/my-tickets/')

        returned_order_ids = [ticket['order_id'] for ticket in response.data]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(returned_order_ids, [own_order.id])
        self.assertEqual(response.data[0]['event_title'], self.event.title)
        self.assertTrue(response.data[0]['qr_code'])


class TicketAuthenticationTests(OrderTestBase):
    def test_unauthenticated_user_cannot_read_ticket_wallet(self):
        response = self.client.get('/api/orders/my-tickets/')

        self.assertEqual(response.status_code, 401)
