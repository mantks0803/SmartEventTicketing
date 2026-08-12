from datetime import datetime
from decimal import Decimal

from django.utils import timezone

from authentication.models import User
from events.models import EventCategoryEnum, TicketType
from orders.models import Order, OrderItem, OrderStatusEnum, Ticket
from seating.models import Seat

from .base import OrderTestBase


class AdminRevenueReportTests(OrderTestBase):
    def setUp(self):
        super().setUp()

        self.admin_user = User.objects.create_user(
            username='admin-report',
            email='admin-report@example.com',
            phone_number='0903999999',
            name='Admin Report',
            type='ADMIN',
            password='123456',
        )

        self.other_organizer = self.create_organizer(8)
        self.workshop_event = self.create_event(
            'Workshop Event',
            organizer=self.other_organizer,
        )
        self.workshop_event.category = EventCategoryEnum.WORKSHOP
        self.workshop_event.save(update_fields=['category'])

        workshop_ticket_type = TicketType.objects.create(
            event=self.workshop_event,
            name='Standard',
            price=150000,
            quantity=2,
        )
        workshop_seats = [
            Seat.objects.create(
                event=self.workshop_event,
                ticket_type=workshop_ticket_type,
                row='W',
                number=number,
            )
            for number in range(1, 3)
        ]

        # Arrange: đơn PAID tháng 1 có một vé và đã check-in.
        self.music_order = Order.objects.create(
            customer=self.customer,
            event=self.event,
            total_amount=Decimal('100000.00'),
            status=OrderStatusEnum.PAID,
        )
        OrderItem.objects.create(
            order=self.music_order,
            seat=self.seats[0],
            ticket_type=self.ticket_type,
            unit_price=Decimal('100000.00'),
        )
        Ticket.objects.create(
            order=self.music_order,
            seat=self.seats[0],
            ticket_type=self.ticket_type,
            qr_code='ADMIN-REPORT-MUSIC',
            is_checked_in=True,
            checked_in_at=timezone.now(),
        )

        # Arrange: đơn PAID tháng 2 có hai vé của Organizer khác.
        second_customer = self.create_customer(8)
        self.workshop_order = Order.objects.create(
            customer=second_customer,
            event=self.workshop_event,
            total_amount=Decimal('300000.00'),
            status=OrderStatusEnum.PAID,
        )
        for index, seat in enumerate(workshop_seats, start=1):
            OrderItem.objects.create(
                order=self.workshop_order,
                seat=seat,
                ticket_type=workshop_ticket_type,
                unit_price=Decimal('150000.00'),
            )
            Ticket.objects.create(
                order=self.workshop_order,
                seat=seat,
                ticket_type=workshop_ticket_type,
                qr_code=f'ADMIN-REPORT-WORKSHOP-{index}',
            )

        # Đơn PENDING không được xuất hiện trong bất kỳ số liệu doanh thu nào.
        pending_order = Order.objects.create(
            customer=self.customer,
            event=self.event,
            total_amount=Decimal('900000.00'),
            status=OrderStatusEnum.PENDING,
        )
        OrderItem.objects.create(
            order=pending_order,
            seat=self.seats[2],
            ticket_type=self.ticket_type,
            unit_price=Decimal('900000.00'),
        )

        january = timezone.make_aware(datetime(2026, 1, 15, 10, 0))
        february = timezone.make_aware(datetime(2026, 2, 10, 10, 0))
        Order.objects.filter(id=self.music_order.id).update(created_at=january)
        Order.objects.filter(id=self.workshop_order.id).update(
            created_at=february,
        )

        self.report_url = '/api/orders/admin/revenue-report/'
        self.filter_url = '/api/orders/admin/revenue-report/filters/'

    def test_admin_can_view_system_revenue_report(self):
        self.client.force_authenticate(self.admin_user)

        # Act: Admin xem báo cáo không truyền bộ lọc.
        response = self.client.get(self.report_url)

        # Assert: chỉ hai đơn PAID được tổng hợp.
        self.assertEqual(response.status_code, 200)
        overview = response.data['overview']
        self.assertEqual(overview['total_revenue'], '400000.00')
        self.assertEqual(overview['total_paid_orders'], 2)
        self.assertEqual(overview['total_tickets_sold'], 3)
        self.assertEqual(overview['total_events'], 2)
        self.assertEqual(overview['total_checked_in'], 1)

        self.assertEqual(
            [row['month'] for row in response.data['revenue_by_month']],
            ['2026-01', '2026-02'],
        )
        self.assertEqual(
            response.data['revenue_by_organizer'][0]['total_revenue'],
            '300000.00',
        )
        self.assertEqual(
            response.data['revenue_by_event'][0]['event_id'],
            self.workshop_event.id,
        )

    def test_filters_are_combined_with_and_condition(self):
        self.client.force_authenticate(self.admin_user)

        response = self.client.get(self.report_url, {
            'event_id': self.event.id,
            'organizer_id': self.organizer.pk,
            'category': EventCategoryEnum.MUSIC,
            'date_from': '2026-01-15',
            'date_to': '2026-01-15',
        })

        self.assertEqual(response.status_code, 200)
        overview = response.data['overview']
        self.assertEqual(overview['total_revenue'], '100000.00')
        self.assertEqual(overview['total_paid_orders'], 1)
        self.assertEqual(overview['total_tickets_sold'], 1)
        self.assertEqual(overview['total_events'], 1)
        self.assertEqual(len(response.data['revenue_by_month']), 1)
        self.assertEqual(
            response.data['revenue_by_category'][0]['category'],
            EventCategoryEnum.MUSIC,
        )

    def test_invalid_query_params_return_bad_request(self):
        self.client.force_authenticate(self.admin_user)

        invalid_params = [
            {'event_id': 'abc'},
            {'organizer_id': '0'},
            {'category': 'INVALID'},
            {'date_from': 'not-a-date'},
            {'date_from': '2026-03-01', 'date_to': '2026-02-01'},
        ]

        for params in invalid_params:
            with self.subTest(params=params):
                response = self.client.get(self.report_url, params)
                self.assertEqual(response.status_code, 400)

    def test_empty_filter_returns_zero_values_and_empty_charts(self):
        self.client.force_authenticate(self.admin_user)

        response = self.client.get(self.report_url, {
            'date_from': '2030-01-01',
            'date_to': '2030-12-31',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['overview']['total_revenue'], '0.00')
        self.assertEqual(response.data['overview']['total_paid_orders'], 0)
        self.assertEqual(response.data['overview']['total_tickets_sold'], 0)
        self.assertEqual(response.data['overview']['total_events'], 0)
        self.assertEqual(response.data['overview']['total_checked_in'], 0)
        self.assertEqual(response.data['revenue_by_month'], [])
        self.assertEqual(response.data['revenue_by_category'], [])
        self.assertEqual(response.data['revenue_by_organizer'], [])
        self.assertEqual(response.data['revenue_by_event'], [])

    def test_filter_endpoint_returns_dropdown_data(self):
        self.client.force_authenticate(self.admin_user)

        response = self.client.get(self.filter_url)

        self.assertEqual(response.status_code, 200)
        event_ids = [event['id'] for event in response.data['events']]
        organizer_ids = [
            organizer['id']
            for organizer in response.data['organizers']
        ]
        category_values = [
            category['value']
            for category in response.data['categories']
        ]

        self.assertIn(self.workshop_event.id, event_ids)
        self.assertIn(self.other_organizer.pk, organizer_ids)
        self.assertIn(EventCategoryEnum.MUSIC, category_values)
        self.assertIn(EventCategoryEnum.WORKSHOP, category_values)

    def test_non_admin_users_cannot_view_report(self):
        self.client.force_authenticate(self.customer.user)
        customer_response = self.client.get(self.report_url)
        customer_filter_response = self.client.get(self.filter_url)

        self.client.force_authenticate(self.organizer_user)
        organizer_response = self.client.get(self.report_url)
        organizer_filter_response = self.client.get(self.filter_url)

        self.client.force_authenticate(user=None)
        anonymous_response = self.client.get(self.report_url)
        anonymous_filter_response = self.client.get(self.filter_url)

        self.assertEqual(customer_response.status_code, 403)
        self.assertEqual(customer_filter_response.status_code, 403)
        self.assertEqual(organizer_response.status_code, 403)
        self.assertEqual(organizer_filter_response.status_code, 403)
        self.assertEqual(anonymous_response.status_code, 401)
        self.assertEqual(anonymous_filter_response.status_code, 401)
