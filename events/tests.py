from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APITestCase

from authentication.models import Customer, Organizer, User
from events.models import Event, EventStatusEnum, TicketType
from seating.models import Seat


class OrganizerEventTests(APITestCase):
    def setUp(self):
        self.organizer_user = User.objects.create_user(
            username='organizer_test',
            email='organizer_test@example.com',
            phone_number='0900000101',
            name='Organizer Test',
            type='ORGANIZER',
            password='123456'
        )

        self.organizer = Organizer.objects.create(
            user=self.organizer_user,
            company_name='Công ty Test',
            bank_account='123456789'
        )

        self.customer_user = User.objects.create_user(
            username='customer_test',
            email='customer_test@example.com',
            phone_number='0900000102',
            name='Customer Test',
            type='CUSTOMER',
            password='123456'
        )

        Customer.objects.create(user=self.customer_user)

        self.payload = {
            'title': 'Sự kiện Test',
            'thumbnail': 'https://example.com/event.jpg',
            'description': 'Mô tả sự kiện test',
            'location': 'TP.HCM',
            'start_time': (
                timezone.now() + timedelta(days=7)
            ).isoformat(),
            'category': 'MUSIC',
            'ticket_types': [
                {
                    'name': 'VIP',
                    'price': 500000,
                    'total_rows': 2,
                    'seats_per_row': 5,
                    'row_prefix': 'VIP'
                },
                {
                    'name': 'Phổ thông',
                    'price': 200000,
                    'total_rows': 3,
                    'seats_per_row': 10,
                    'row_prefix': 'A'
                }
            ]
        }

    def test_organizer_can_create_event(self):
        self.client.force_authenticate(self.organizer_user)

        response = self.client.post(
            '/api/events/create/',
            self.payload,
            format='json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(TicketType.objects.count(), 2)
        self.assertEqual(Seat.objects.count(), 40)

        event = Event.objects.first()

        self.assertEqual(event.organizer, self.organizer)
        self.assertEqual(event.status, EventStatusEnum.PENDING)
        self.assertEqual(event.seats.filter(row='VIP1').count(), 5)
        self.assertEqual(event.seats.filter(row='A1').count(), 10)

    def test_customer_cannot_create_event(self):
        self.client.force_authenticate(self.customer_user)

        response = self.client.post(
            '/api/events/create/',
            self.payload,
            format='json'
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Event.objects.count(), 0)

    def test_duplicate_rows_are_rejected(self):
        self.client.force_authenticate(self.organizer_user)

        self.payload['ticket_types'][1]['row_prefix'] = 'VIP'

        response = self.client.post(
            '/api/events/create/',
            self.payload,
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Event.objects.count(), 0)
        self.assertEqual(Seat.objects.count(), 0)

    def test_organizer_only_sees_own_events(self):
        other_user = User.objects.create_user(
            username='other_organizer',
            email='other_organizer@example.com',
            phone_number='0900000103',
            name='Other Organizer',
            type='ORGANIZER',
            password='123456'
        )

        other_organizer = Organizer.objects.create(
            user=other_user,
            company_name='Công ty khác',
            bank_account='987654321'
        )

        Event.objects.create(
            organizer=self.organizer,
            title='Sự kiện của tôi',
            thumbnail='https://example.com/mine.jpg',
            description='Test',
            location='TP.HCM',
            start_time=timezone.now() + timedelta(days=1)
        )

        Event.objects.create(
            organizer=other_organizer,
            title='Sự kiện của người khác',
            thumbnail='https://example.com/other.jpg',
            description='Test',
            location='TP.HCM',
            start_time=timezone.now() + timedelta(days=1)
        )

        self.client.force_authenticate(self.organizer_user)

        response = self.client.get(
            '/api/events/organizer/events/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]['title'],
            'Sự kiện của tôi'
        )
