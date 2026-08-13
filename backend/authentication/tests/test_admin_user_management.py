from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from rest_framework.test import APITestCase

from authentication.models import Customer, Organizer, User, UserType
from events.models import Event, EventStatusEnum, TicketType
from orders.models import Order, OrderItem, OrderStatusEnum, Ticket
from seating.models import Seat, SeatStatusEnum


class AdminUserManagementTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='user-admin',
            email='user-admin@example.com',
            phone_number='0911000001',
            name='User Admin',
            type=UserType.ADMIN,
            password='123456',
        )
        self.customer_user = User.objects.create_user(
            username='customer-one',
            email='customer-one@example.com',
            phone_number='0911000002',
            name='Customer One',
            type=UserType.CUSTOMER,
            password='123456',
        )
        self.customer = Customer.objects.create(user=self.customer_user)
        self.organizer_user = User.objects.create_user(
            username='organizer-one',
            email='organizer-one@example.com',
            phone_number='0911000003',
            name='Organizer One',
            type=UserType.ORGANIZER,
            password='123456',
        )
        self.organizer = Organizer.objects.create(
            user=self.organizer_user,
            company_name='Organizer Company',
            bank_account='123456789',
        )
        self.locked_user = User.objects.create_user(
            username='locked-user',
            email='locked-user@example.com',
            phone_number='0911000004',
            name='Locked User',
            type=UserType.CUSTOMER,
            status=False,
            is_active=False,
            password='123456',
        )
        self.superuser = User.objects.create_superuser(
            username='protected-superuser',
            email='protected-superuser@example.com',
            phone_number='0911000005',
            name='Protected Superuser',
            password='123456',
        )
        self.client.force_authenticate(self.admin)

    def test_admin_can_search_filter_and_paginate_users(self):
        search_response = self.client.get(
            '/api/auth/admin/users/?search=customer-one'
        )
        self.assertEqual(search_response.status_code, 200)
        self.assertEqual(search_response.data['count'], 1)
        self.assertEqual(
            search_response.data['results'][0]['id'],
            self.customer_user.id,
        )

        locked_response = self.client.get(
            '/api/auth/admin/users/?account_status=LOCKED'
        )
        self.assertEqual(locked_response.status_code, 200)
        self.assertEqual(locked_response.data['count'], 1)
        self.assertEqual(
            locked_response.data['results'][0]['account_status'],
            'LOCKED',
        )

        page_response = self.client.get(
            '/api/auth/admin/users/?page=1&page_size=2'
        )
        self.assertEqual(page_response.status_code, 200)
        self.assertEqual(page_response.data['count'], 5)
        self.assertEqual(len(page_response.data['results']), 2)

    def test_staff_user_is_filtered_and_displayed_as_admin(self):
        staff_user = User.objects.create_user(
            username='staff-customer',
            email='staff-customer@example.com',
            phone_number='0911000006',
            name='Staff Customer',
            type=UserType.CUSTOMER,
            is_staff=True,
            password='123456',
        )

        admin_response = self.client.get(
            '/api/auth/admin/users/?role=ADMIN&page_size=100'
        )
        customer_response = self.client.get(
            '/api/auth/admin/users/?role=CUSTOMER&page_size=100'
        )

        admin_ids = [item['id'] for item in admin_response.data['results']]
        customer_ids = [
            item['id'] for item in customer_response.data['results']
        ]
        staff_row = next(
            item
            for item in admin_response.data['results']
            if item['id'] == staff_user.id
        )

        self.assertIn(staff_user.id, admin_ids)
        self.assertNotIn(staff_user.id, customer_ids)
        self.assertEqual(staff_row['role'], UserType.ADMIN)

    def test_summary_uses_effective_roles_and_both_status_fields(self):
        response = self.client.get('/api/auth/admin/users/summary/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_users'], 5)
        self.assertEqual(response.data['total_customers'], 2)
        self.assertEqual(response.data['total_organizers'], 1)
        self.assertEqual(response.data['total_admins'], 2)
        self.assertEqual(response.data['total_locked'], 1)

    def test_customer_detail_contains_profile_and_paid_statistics(self):
        event = Event.objects.create(
            organizer=self.organizer,
            title='Detail Test Event',
            thumbnail='https://example.com/event.jpg',
            description='Event for user detail test',
            location='TP.HCM',
            start_time=timezone.now() + timedelta(days=2),
            status=EventStatusEnum.PUBLISHED,
        )
        ticket_type = TicketType.objects.create(
            event=event,
            name='VIP',
            price=100000,
            quantity=1,
        )
        seat = Seat.objects.create(
            event=event,
            ticket_type=ticket_type,
            row='A',
            number=1,
            status=SeatStatusEnum.SOLD,
        )
        paid_order = Order.objects.create(
            customer=self.customer,
            event=event,
            total_amount=Decimal('100000.00'),
            status=OrderStatusEnum.PAID,
        )
        Order.objects.create(
            customer=self.customer,
            event=event,
            total_amount=Decimal('50000.00'),
            status=OrderStatusEnum.PENDING,
        )
        OrderItem.objects.create(
            order=paid_order,
            seat=seat,
            ticket_type=ticket_type,
            unit_price=Decimal('100000.00'),
        )
        Ticket.objects.create(
            order=paid_order,
            seat=seat,
            ticket_type=ticket_type,
            qr_code='ADMIN-USER-DETAIL-TICKET',
        )

        response = self.client.get(
            f'/api/auth/admin/users/{self.customer_user.id}/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['customer_profile']['tier'], 'MEMBER')
        self.assertEqual(response.data['statistics']['total_orders'], 2)
        self.assertEqual(response.data['statistics']['paid_orders'], 1)
        self.assertEqual(response.data['statistics']['total_tickets'], 1)
        self.assertEqual(
            response.data['statistics']['total_paid_amount'],
            Decimal('100000.00'),
        )

    def test_missing_role_profile_does_not_cause_server_error(self):
        missing_profile_user = User.objects.create_user(
            username='missing-organizer-profile',
            email='missing-organizer@example.com',
            phone_number='0911000007',
            name='Missing Organizer',
            type=UserType.ORGANIZER,
            password='123456',
        )

        response = self.client.get(
            f'/api/auth/admin/users/{missing_profile_user.id}/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data['organizer_profile'])
        self.assertEqual(response.data['statistics']['total_events'], 0)
        self.assertEqual(response.data['statistics']['total_revenue'], 0)

    def test_lock_and_unlock_update_both_account_flags(self):
        lock_response = self.client.post(
            f'/api/auth/admin/users/{self.customer_user.id}/lock/'
        )

        self.customer_user.refresh_from_db()
        self.assertEqual(lock_response.status_code, 200)
        self.assertFalse(self.customer_user.status)
        self.assertFalse(self.customer_user.is_active)
        self.assertEqual(
            lock_response.data['user']['account_status'],
            'LOCKED',
        )

        unlock_response = self.client.post(
            f'/api/auth/admin/users/{self.customer_user.id}/unlock/'
        )

        self.customer_user.refresh_from_db()
        self.assertEqual(unlock_response.status_code, 200)
        self.assertTrue(self.customer_user.status)
        self.assertTrue(self.customer_user.is_active)

    def test_lock_protects_current_admin_and_other_admin_accounts(self):
        other_admin = User.objects.create_user(
            username='other-admin',
            email='other-admin@example.com',
            phone_number='0911000008',
            name='Other Admin',
            type=UserType.ADMIN,
            password='123456',
        )
        self_response = self.client.post(
            f'/api/auth/admin/users/{self.admin.id}/lock/'
        )
        superuser_response = self.client.post(
            f'/api/auth/admin/users/{self.superuser.id}/lock/'
        )
        other_admin_response = self.client.post(
            f'/api/auth/admin/users/{other_admin.id}/lock/'
        )

        self.assertEqual(self_response.status_code, 400)
        self.assertEqual(self_response.data['code'], 'cannot_lock_self')
        self.assertEqual(superuser_response.status_code, 400)
        self.assertEqual(
            superuser_response.data['code'],
            'cannot_change_admin_status',
        )
        self.assertEqual(other_admin_response.status_code, 400)
        self.assertEqual(
            other_admin_response.data['code'],
            'cannot_change_admin_status',
        )

    def test_lock_and_unlock_repair_half_locked_account(self):
        self.customer_user.status = False
        self.customer_user.is_active = True
        self.customer_user.save(update_fields=['status', 'is_active'])

        lock_response = self.client.post(
            f'/api/auth/admin/users/{self.customer_user.id}/lock/'
        )
        self.customer_user.refresh_from_db()

        self.assertEqual(lock_response.status_code, 200)
        self.assertFalse(self.customer_user.status)
        self.assertFalse(self.customer_user.is_active)

        self.customer_user.status = True
        self.customer_user.is_active = False
        self.customer_user.save(update_fields=['status', 'is_active'])

        unlock_response = self.client.post(
            f'/api/auth/admin/users/{self.customer_user.id}/unlock/'
        )
        self.customer_user.refresh_from_db()

        self.assertEqual(unlock_response.status_code, 200)
        self.assertTrue(self.customer_user.status)
        self.assertTrue(self.customer_user.is_active)

    def test_repeated_status_change_returns_conflict(self):
        lock_response = self.client.post(
            f'/api/auth/admin/users/{self.locked_user.id}/lock/'
        )
        unlock_response = self.client.post(
            f'/api/auth/admin/users/{self.customer_user.id}/unlock/'
        )

        self.assertEqual(lock_response.status_code, 409)
        self.assertEqual(unlock_response.status_code, 409)

    def test_invalid_filters_and_missing_user_return_clear_errors(self):
        invalid_urls = [
            '/api/auth/admin/users/?role=INVALID',
            '/api/auth/admin/users/?account_status=INVALID',
            '/api/auth/admin/users/?page=0',
            '/api/auth/admin/users/?page_size=101',
        ]

        for url in invalid_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 400)

        missing_response = self.client.get('/api/auth/admin/users/999999/')
        self.assertEqual(missing_response.status_code, 404)

    def test_non_admin_cannot_access_user_management(self):
        self.client.force_authenticate(self.customer_user)
        customer_response = self.client.get('/api/auth/admin/users/')
        self.client.force_authenticate(user=None)
        anonymous_response = self.client.get('/api/auth/admin/users/')

        self.assertEqual(customer_response.status_code, 403)
        self.assertEqual(anonymous_response.status_code, 401)

    def test_status_false_user_cannot_login(self):
        self.customer_user.status = False
        self.customer_user.save(update_fields=['status'])
        self.client.force_authenticate(user=None)

        response = self.client.post(
            '/api/auth/login/',
            {
                'email': self.customer_user.email,
                'password': '123456',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertNotIn('access', response.data)

    def test_status_false_user_cannot_use_existing_authenticated_session(self):
        self.customer_user.status = False
        self.customer_user.save(update_fields=['status'])
        self.client.force_authenticate(self.customer_user)

        response = self.client.get('/api/auth/me/')

        self.assertEqual(response.status_code, 403)
