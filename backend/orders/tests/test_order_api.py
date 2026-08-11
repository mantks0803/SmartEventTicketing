from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APIClient

from orders.models import Order, OrderStatusEnum
from orders.services import hold_seats
from seating.models import SeatStatusEnum

from .base import OrderTestBase


class OrderApiTests(OrderTestBase):
    def test_customer_can_hold_seat_for_ten_minutes(self):
        self.client.force_authenticate(self.customer.user)
        before_request = timezone.now()

        # Act: gọi đúng API mà frontend sử dụng khi bấm giữ ghế.
        response = self.client.post(
            '/api/orders/hold/',
            {'seat_ids': [self.seats[0].id]},
            format='json',
        )

        # Assert: đơn tồn tại và hạn giữ ghế xấp xỉ 10 phút.
        self.assertEqual(response.status_code, 201)
        order = Order.objects.get(id=response.data['id'])
        self.assertEqual(order.status, OrderStatusEnum.PENDING)
        self.assertGreaterEqual(
            order.expires_at,
            before_request + timedelta(minutes=9, seconds=50),
        )
        self.assertLessEqual(
            order.expires_at,
            before_request + timedelta(minutes=10, seconds=10),
        )
        self.seats[0].refresh_from_db()
        self.assertEqual(self.seats[0].status, SeatStatusEnum.LOCKED)

    def test_duplicate_seat_ids_are_rejected(self):
        self.client.force_authenticate(self.customer.user)

        response = self.client.post(
            '/api/orders/hold/',
            {'seat_ids': [self.seats[0].id, self.seats[0].id]},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)

    def test_organizer_cannot_hold_seat(self):
        self.client.force_authenticate(self.organizer_user)

        response = self.client.post(
            '/api/orders/hold/',
            {'seat_ids': [self.seats[0].id]},
            format='json',
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Order.objects.count(), 0)

    def test_customer_cannot_read_or_cancel_another_customers_order(self):
        order = hold_seats(self.customer, [self.seats[0].id])
        other_customer = self.create_customer(1)
        other_client = APIClient()
        other_client.force_authenticate(other_customer.user)

        detail_response = other_client.get(f'/api/orders/{order.id}/')
        cancel_response = other_client.post(f'/api/orders/{order.id}/cancel/')

        order.refresh_from_db()
        self.assertEqual(detail_response.status_code, 404)
        self.assertEqual(cancel_response.status_code, 404)
        self.assertEqual(order.status, OrderStatusEnum.PENDING)
