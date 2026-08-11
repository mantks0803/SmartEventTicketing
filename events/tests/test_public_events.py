from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APITestCase

from authentication.models import Organizer, User
from events.models import Event, EventStatusEnum


class PublicEventTests(APITestCase):
    def setUp(self):
        organizer_user = User.objects.create_user(
            username='public-event-organizer',
            email='public-event-organizer@example.com',
            phone_number='0902000001',
            name='Public Event Organizer',
            type='ORGANIZER',
            password='123456',
        )
        self.organizer = Organizer.objects.create(
            user=organizer_user,
            company_name='Public Event Company',
            bank_account='123456789',
        )
        self.published_event = self.create_event(
            title='Acoustic Night',
            location='TP.HCM',
            category='MUSIC',
            status=EventStatusEnum.PUBLISHED,
        )
        self.pending_event = self.create_event(
            title='Pending Music',
            location='Ha Noi',
            category='MUSIC',
            status=EventStatusEnum.PENDING,
        )
        self.cancelled_event = self.create_event(
            title='Cancelled Workshop',
            location='Da Nang',
            category='WORKSHOP',
            status=EventStatusEnum.CANCELLED,
        )

    def create_event(
        self,
        title,
        location='TP.HCM',
        category='MUSIC',
        status=EventStatusEnum.PUBLISHED,
        start_time=None,
    ):
        return Event.objects.create(
            organizer=self.organizer,
            title=title,
            thumbnail='https://example.com/event.jpg',
            description='Mo ta su kien',
            location=location,
            start_time=start_time or timezone.now() + timedelta(days=7),
            category=category,
            status=status,
        )

    def test_public_list_only_returns_published_events(self):
        # Act: người dùng không cần đăng nhập gọi danh sách sự kiện.
        response = self.client.get('/api/events/')

        # Assert: chỉ sự kiện đã được admin duyệt mới xuất hiện.
        returned_ids = [event['id'] for event in response.data['results']]
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.published_event.id, returned_ids)
        self.assertNotIn(self.pending_event.id, returned_ids)
        self.assertNotIn(self.cancelled_event.id, returned_ids)

    def test_event_list_is_paginated(self):
        for index in range(12):
            self.create_event(title=f'Published Event {index + 1}')

        first_page = self.client.get('/api/events/?page=1')
        second_page = self.client.get('/api/events/?page=2')

        self.assertEqual(first_page.status_code, 200)
        self.assertEqual(first_page.data['count'], 13)
        self.assertEqual(len(first_page.data['results']), 12)
        self.assertEqual(second_page.status_code, 200)
        self.assertEqual(len(second_page.data['results']), 1)

    def test_search_matches_title_or_location(self):
        workshop = self.create_event(
            title='Vue Workshop',
            location='Da Nang',
            category='WORKSHOP',
        )

        title_response = self.client.get('/api/events/?search=Vue')
        location_response = self.client.get('/api/events/?search=Da%20Nang')

        self.assertEqual(title_response.status_code, 200)
        self.assertEqual(title_response.data['results'][0]['id'], workshop.id)
        self.assertEqual(location_response.status_code, 200)
        self.assertEqual(location_response.data['results'][0]['id'], workshop.id)

    def test_category_filter_only_returns_matching_events(self):
        workshop = self.create_event(
            title='Django Workshop',
            category='WORKSHOP',
        )

        response = self.client.get('/api/events/?category=WORKSHOP')

        returned_ids = [event['id'] for event in response.data['results']]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(returned_ids, [workshop.id])

    def test_non_published_event_detail_is_hidden(self):
        published_response = self.client.get(
            f'/api/events/{self.published_event.id}/'
        )
        pending_response = self.client.get(
            f'/api/events/{self.pending_event.id}/'
        )
        cancelled_response = self.client.get(
            f'/api/events/{self.cancelled_event.id}/'
        )

        self.assertEqual(published_response.status_code, 200)
        self.assertEqual(pending_response.status_code, 404)
        self.assertEqual(cancelled_response.status_code, 404)

    def test_featured_only_returns_future_published_events(self):
        past_event = self.create_event(
            title='Past Event',
            start_time=timezone.now() - timedelta(hours=1),
        )

        response = self.client.get('/api/events/featured/')

        returned_ids = [event['id'] for event in response.data]
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.published_event.id, returned_ids)
        self.assertNotIn(self.pending_event.id, returned_ids)
        self.assertNotIn(past_event.id, returned_ids)
