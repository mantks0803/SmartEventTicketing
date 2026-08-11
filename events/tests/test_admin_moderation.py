from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APITestCase

from authentication.models import Customer, Organizer, User
from events.models import Event, EventStatusEnum


class AdminEventTests(APITestCase):
    def setUp(self):
        organizer_user = User.objects.create_user(
            username='admin-test-organizer',
            email='admin-organizer@example.com',
            phone_number='0902000031',
            name='Admin Test Organizer',
            type='ORGANIZER',
            password='123456',
        )
        self.organizer = Organizer.objects.create(
            user=organizer_user,
            company_name='Admin Test Company',
            bank_account='123456789',
        )
        self.admin_user = User.objects.create_user(
            username='api-admin',
            email='api-admin@example.com',
            phone_number='0902000032',
            name='API Admin',
            type='ADMIN',
            password='123456',
        )
        self.customer_user = User.objects.create_user(
            username='admin-test-customer',
            email='admin-customer@example.com',
            phone_number='0902000033',
            name='Admin Test Customer',
            type='CUSTOMER',
            password='123456',
        )
        Customer.objects.create(user=self.customer_user)
        self.pending_event = Event.objects.create(
            organizer=self.organizer,
            title='Pending Music Event',
            thumbnail='https://example.com/pending.jpg',
            description='Pending event',
            location='TP.HCM',
            start_time=timezone.now() + timedelta(days=2),
        )
        self.published_event = Event.objects.create(
            organizer=self.organizer,
            title='Published Workshop',
            thumbnail='https://example.com/published.jpg',
            description='Published event',
            location='Ha Noi',
            start_time=timezone.now() + timedelta(days=3),
            category='WORKSHOP',
            status=EventStatusEnum.PUBLISHED,
        )

    def test_admin_can_filter_and_search_events(self):
        self.client.force_authenticate(self.admin_user)

        response = self.client.get(
            '/api/events/admin/?status=PENDING&search=Music'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.pending_event.id)

    def test_customer_cannot_access_admin_events(self):
        self.client.force_authenticate(self.customer_user)

        response = self.client.get('/api/events/admin/')

        self.assertEqual(response.status_code, 403)

    def test_admin_can_read_pending_event_detail(self):
        self.client.force_authenticate(self.admin_user)

        response = self.client.get(
            f'/api/events/admin/{self.pending_event.id}/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], EventStatusEnum.PENDING)

    def test_admin_can_approve_pending_event(self):
        self.client.force_authenticate(self.admin_user)

        # Act: admin duyệt event đang PENDING.
        response = self.client.post(
            f'/api/events/admin/{self.pending_event.id}/approve/'
        )

        # Assert: event chuyển sang PUBLISHED và API công khai đọc được.
        self.pending_event.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.pending_event.status, EventStatusEnum.PUBLISHED)
        public_response = self.client.get(
            f'/api/events/{self.pending_event.id}/'
        )
        self.assertEqual(public_response.status_code, 200)

    def test_admin_can_reject_pending_event(self):
        self.client.force_authenticate(self.admin_user)

        response = self.client.post(
            f'/api/events/admin/{self.pending_event.id}/reject/'
        )

        self.pending_event.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.pending_event.status, EventStatusEnum.CANCELLED)

    def test_invalid_admin_transition_returns_conflict(self):
        self.client.force_authenticate(self.admin_user)

        response = self.client.post(
            f'/api/events/admin/{self.published_event.id}/reject/'
        )

        self.published_event.refresh_from_db()
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data['code'], 'event_not_pending')
        self.assertEqual(self.published_event.status, EventStatusEnum.PUBLISHED)

    def test_admin_cannot_approve_started_event(self):
        self.pending_event.start_time = timezone.now() - timedelta(minutes=1)
        self.pending_event.save(update_fields=['start_time'])
        self.client.force_authenticate(self.admin_user)

        response = self.client.post(
            f'/api/events/admin/{self.pending_event.id}/approve/'
        )

        self.pending_event.refresh_from_db()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 'event_already_started')
        self.assertEqual(self.pending_event.status, EventStatusEnum.PENDING)

    def test_staff_user_can_access_admin_events(self):
        staff_user = User.objects.create_user(
            username='staff-admin',
            email='staff-admin@example.com',
            phone_number='0902000034',
            name='Staff Admin',
            type='CUSTOMER',
            is_staff=True,
            password='123456',
        )
        self.client.force_authenticate(staff_user)

        response = self.client.get('/api/events/admin/')

        self.assertEqual(response.status_code, 200)

    def test_pending_event_seats_are_not_public(self):
        response = self.client.get(
            f'/api/seats/event/{self.pending_event.id}/'
        )

        self.assertEqual(response.status_code, 404)
