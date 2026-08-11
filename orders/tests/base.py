from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from authentication.models import Customer, Organizer, User
from events.models import Event, EventStatusEnum, TicketType
from seating.models import Seat


class OrderTestBase(TestCase):
    """Dữ liệu chung, nhỏ gọn cho các test đơn hàng và thanh toán."""

    def setUp(self):
        customer_user = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            phone_number='0903000001',
            name='Customer',
            type='CUSTOMER',
            password='123456',
        )
        self.customer = Customer.objects.create(user=customer_user)

        self.organizer_user = User.objects.create_user(
            username='organizer',
            email='organizer@example.com',
            phone_number='0903000002',
            name='Organizer',
            type='ORGANIZER',
            password='123456',
        )
        self.organizer = Organizer.objects.create(
            user=self.organizer_user,
            company_name='SmartTicket',
            bank_account='123456',
        )

        self.event = self.create_event('Event 1')
        self.other_event = self.create_event('Event 2')
        self.ticket_type = TicketType.objects.create(
            event=self.event,
            name='VIP',
            price=100000,
            quantity=10,
        )
        self.other_ticket_type = TicketType.objects.create(
            event=self.other_event,
            name='VIP',
            price=200000,
            quantity=10,
        )
        self.seats = [
            Seat.objects.create(
                event=self.event,
                ticket_type=self.ticket_type,
                row='A',
                number=number,
            )
            for number in range(1, 7)
        ]
        self.other_seat = Seat.objects.create(
            event=self.other_event,
            ticket_type=self.other_ticket_type,
            row='B',
            number=1,
        )
        self.client = APIClient()

    def create_event(self, title, organizer=None):
        return Event.objects.create(
            organizer=organizer or self.organizer,
            title=title,
            thumbnail='https://example.com/event.jpg',
            description='Test event',
            location='TP.HCM',
            start_time=timezone.now() + timedelta(days=1),
            status=EventStatusEnum.PUBLISHED,
        )

    def create_customer(self, number):
        user = User.objects.create_user(
            username=f'customer-{number}',
            email=f'customer-{number}@example.com',
            phone_number=f'0903001{number:03d}',
            name=f'Customer {number}',
            type='CUSTOMER',
            password='123456',
        )
        return Customer.objects.create(user=user)

    def create_organizer(self, number):
        user = User.objects.create_user(
            username=f'organizer-{number}',
            email=f'organizer-{number}@example.com',
            phone_number=f'0903002{number:03d}',
            name=f'Organizer {number}',
            type='ORGANIZER',
            password='123456',
        )
        organizer = Organizer.objects.create(
            user=user,
            company_name=f'Company {number}',
            bank_account=f'123456{number}',
        )
        return organizer
