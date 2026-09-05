import importlib.util
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from django.db import connection
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIClient

from authentication.models import Customer, Organizer, User, UserType
from events.models import Event, EventCategoryEnum, TicketType
from orders.models import Order, OrderStatusEnum, Payment, Ticket
from seating.models import Seat, SeatStatusEnum


script_path = Path(__file__).resolve().parents[3] / 'database' / 'seed_admin_report_demo.py'
spec = importlib.util.spec_from_file_location('seed_admin_report_demo', script_path)
seed_demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seed_demo)


class SeedAdminReportDemoTests(TestCase):
    def run_seed(self, clear=False):
        output = StringIO()
        with patch.dict(
            connection.settings_dict,
            {'NAME': seed_demo.DEMO_DATABASE_NAME},
        ):
            with redirect_stdout(output):
                seed_demo.run_seed(clear=clear)
        return output.getvalue()

    def test_seed_creates_complete_and_consistent_report_data(self):
        self.run_seed()

        demo_users = User.objects.filter(
            username__startswith=seed_demo.DEMO_USER_PREFIX,
        )
        demo_events = Event.objects.filter(
            title__startswith=seed_demo.DEMO_EVENT_PREFIX,
        )
        demo_orders = Order.objects.filter(event__in=demo_events)
        demo_tickets = Ticket.objects.filter(order__in=demo_orders)

        self.assertEqual(demo_users.count(), 17)
        self.assertEqual(Organizer.objects.filter(user__in=demo_users).count(), 4)
        self.assertEqual(Customer.objects.filter(user__in=demo_users).count(), 12)
        self.assertEqual(demo_events.count(), 8)
        self.assertEqual(TicketType.objects.filter(event__in=demo_events).count(), 16)
        self.assertEqual(Seat.objects.filter(event__in=demo_events).count(), 400)
        self.assertEqual(demo_orders.count(), 60)
        self.assertEqual(Payment.objects.filter(order__in=demo_orders).count(), 60)
        self.assertEqual(demo_tickets.count(), 120)
        self.assertEqual(demo_tickets.filter(is_checked_in=True).count(), 72)
        self.assertEqual(
            Seat.objects.filter(
                event__in=demo_events,
                status=SeatStatusEnum.SOLD,
            ).count(),
            120,
        )

        months = (
            demo_orders
            .annotate(month=TruncMonth('created_at'))
            .values_list('month', flat=True)
            .distinct()
        )
        self.assertEqual(len(months), 6)
        self.assertEqual(
            set(demo_events.values_list('category', flat=True)),
            set(EventCategoryEnum.values),
        )

        for order in demo_orders.prefetch_related(
            'items',
            'payments',
            'tickets__seat',
        ):
            item_total = order.items.aggregate(total=Sum('unit_price'))['total']
            payment = order.payments.get()

            self.assertEqual(order.status, OrderStatusEnum.PAID)
            self.assertEqual(order.total_amount, item_total)
            self.assertEqual(payment.amount, order.total_amount)
            self.assertEqual(order.items.count(), order.tickets.count())
            self.assertLess(order.created_at, order.event.start_time)

            for ticket in order.tickets.all():
                self.assertEqual(ticket.seat.status, SeatStatusEnum.SOLD)
                if ticket.is_checked_in:
                    self.assertGreaterEqual(
                        ticket.checked_in_at,
                        order.event.start_time,
                    )

        admin = User.objects.get(username='report_demo_admin')
        organizer_user = User.objects.get(
            username='report_demo_organizer_1',
        )
        self.assertEqual(admin.type, UserType.ADMIN)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.check_password(seed_demo.ADMIN_PASSWORD))
        self.assertTrue(organizer_user.check_password(seed_demo.ORGANIZER_PASSWORD))

        client = APIClient()
        client.force_authenticate(admin)
        response = client.get('/api/orders/admin/revenue-report/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['overview']['total_paid_orders'], 60)
        self.assertEqual(response.data['overview']['total_tickets_sold'], 120)
        self.assertEqual(response.data['overview']['total_checked_in'], 72)
        self.assertEqual(response.data['overview']['total_events'], 8)
        self.assertEqual(len(response.data['revenue_by_month']), 6)
        self.assertEqual(len(response.data['revenue_by_category']), 4)
        self.assertEqual(len(response.data['revenue_by_organizer']), 4)
        self.assertEqual(len(response.data['revenue_by_event']), 8)

    def test_clear_only_removes_demo_data(self):
        normal_user = User.objects.create_user(
            username='normal_user',
            email='normal@example.com',
            phone_number='0909000000',
            name='Normal User',
            password='NormalUser@123',
        )
        self.run_seed()

        self.run_seed(clear=True)

        self.assertTrue(User.objects.filter(id=normal_user.id).exists())
        self.assertFalse(
            User.objects.filter(
                username__startswith=seed_demo.DEMO_USER_PREFIX,
            ).exists()
        )
        self.assertFalse(
            Event.objects.filter(
                title__startswith=seed_demo.DEMO_EVENT_PREFIX,
            ).exists()
        )

    def test_seed_refuses_to_duplicate_existing_demo_data(self):
        self.run_seed()

        with self.assertRaisesMessage(ValueError, 'Dữ liệu demo đã tồn tại'):
            self.run_seed()

        self.assertEqual(Order.objects.count(), 60)
        self.assertEqual(Ticket.objects.count(), 120)


class SeedAdminReportDemoSafetyTests(SimpleTestCase):
    def test_seed_and_clear_refuse_to_run_on_main_database(self):
        with patch.dict(
            connection.settings_dict,
            {'NAME': 'smart_booking_db'},
        ):
            for clear in (False, True):
                with self.subTest(clear=clear):
                    with self.assertRaisesMessage(ValueError, 'Script chỉ được chạy'):
                        seed_demo.run_seed(clear=clear)

    def test_import_does_not_register_a_django_management_command(self):
        self.assertFalse(hasattr(seed_demo, 'Command'))
        self.assertTrue(callable(seed_demo.run_seed))
