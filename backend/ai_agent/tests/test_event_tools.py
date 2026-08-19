from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from ai_agent.models import (
    EventService,
    PricingUnitEnum,
    QualityLevelEnum,
    ServiceCategoryEnum,
)
from ai_agent.rag_engine.event_tools import (
    check_event_availability,
    estimate_event_budget,
    recommend_events,
    suggest_ticket_price,
)
from authentication.models import Organizer, User
from events.models import (
    Event,
    EventCategoryEnum,
    EventStatusEnum,
    TicketType,
)
from seating.models import Seat, SeatStatusEnum


class EventToolsTests(TestCase):
    def setUp(self):
        self.organizer_user = User.objects.create_user(
            username='event-tools-organizer',
            email='event-tools@example.com',
            phone_number='0909000001',
            name='Event Tools Organizer',
            type='ORGANIZER',
            password='123456',
        )
        self.organizer = Organizer.objects.create(
            user=self.organizer_user,
            company_name='Event Tools Company',
            bank_account='123456789',
        )

    def create_event(
        self,
        title,
        start_time=None,
        category=EventCategoryEnum.MUSIC,
        status=EventStatusEnum.PUBLISHED,
        location='TP.HCM',
    ):
        return Event.objects.create(
            organizer=self.organizer,
            title=title,
            thumbnail='https://example.com/event.jpg',
            description='Sự kiện dùng trong test event tools.',
            location=location,
            start_time=(
                start_time
                or timezone.now() + timedelta(days=7)
            ),
            category=category,
            status=status,
        )

    def create_ticket_type_with_seats(
        self,
        event,
        name,
        price,
        seat_statuses,
        row_prefix,
    ):
        ticket_type = TicketType.objects.create(
            event=event,
            name=name,
            price=price,
            quantity=len(seat_statuses),
        )

        for number, seat_status in enumerate(
            seat_statuses,
            start=1,
        ):
            Seat.objects.create(
                event=event,
                ticket_type=ticket_type,
                row=row_prefix,
                number=number,
                status=seat_status,
            )

        return ticket_type

    def create_service(
        self,
        code,
        name,
        category,
        pricing_unit,
        min_price,
        max_price,
        location='TP.HCM',
        quality_level=QualityLevelEnum.STANDARD,
        min_capacity=1,
        max_capacity=1000,
    ):
        return EventService.objects.create(
            code=code,
            name=name,
            provider_name='Nhà cung cấp test',
            category=category,
            quality_level=quality_level,
            location=location,
            pricing_unit=pricing_unit,
            min_price=min_price,
            max_price=max_price,
            min_capacity=min_capacity,
            max_capacity=max_capacity,
            included_duration_hours=None,
            description='Dịch vụ dùng trong unit test.',
            source_url='',
            verified_at=date(2026, 8, 17),
            is_active=True,
        )

    def test_recommend_events_excludes_invalid_events_and_filters(self):
        now = timezone.now()

        eligible_event = self.create_event(
            title='Concert TP.HCM',
            start_time=now + timedelta(days=7),
            category=EventCategoryEnum.MUSIC,
            location='Quận 1, TP.HCM',
        )
        self.create_ticket_type_with_seats(
            event=eligible_event,
            name='Thường',
            price=Decimal('200000.00'),
            seat_statuses=[
                SeatStatusEnum.AVAILABLE,
                SeatStatusEnum.AVAILABLE,
                SeatStatusEnum.SOLD,
            ],
            row_prefix='A',
        )
        self.create_ticket_type_with_seats(
            event=eligible_event,
            name='VIP',
            price=Decimal('500000.00'),
            seat_statuses=[SeatStatusEnum.AVAILABLE],
            row_prefix='VIP',
        )

        other_valid_event = self.create_event(
            title='Workshop Hà Nội',
            start_time=now + timedelta(days=14),
            category=EventCategoryEnum.WORKSHOP,
            location='Hà Nội',
        )
        self.create_ticket_type_with_seats(
            event=other_valid_event,
            name='Workshop',
            price=Decimal('700000.00'),
            seat_statuses=[SeatStatusEnum.AVAILABLE],
            row_prefix='W',
        )

        pending_event = self.create_event(
            title='Event Pending',
            status=EventStatusEnum.PENDING,
        )
        self.create_ticket_type_with_seats(
            event=pending_event,
            name='Pending Ticket',
            price=Decimal('100000.00'),
            seat_statuses=[SeatStatusEnum.AVAILABLE],
            row_prefix='P',
        )

        cancelled_event = self.create_event(
            title='Event Cancelled',
            status=EventStatusEnum.CANCELLED,
        )
        self.create_ticket_type_with_seats(
            event=cancelled_event,
            name='Cancelled Ticket',
            price=Decimal('100000.00'),
            seat_statuses=[SeatStatusEnum.AVAILABLE],
            row_prefix='C',
        )

        past_event = self.create_event(
            title='Event đã diễn ra',
            start_time=now - timedelta(days=1),
        )
        self.create_ticket_type_with_seats(
            event=past_event,
            name='Past Ticket',
            price=Decimal('100000.00'),
            seat_statuses=[SeatStatusEnum.AVAILABLE],
            row_prefix='OLD',
        )

        sold_out_event = self.create_event(
            title='Event hết ghế',
            start_time=now + timedelta(days=5),
        )
        self.create_ticket_type_with_seats(
            event=sold_out_event,
            name='Sold Out Ticket',
            price=Decimal('100000.00'),
            seat_statuses=[
                SeatStatusEnum.SOLD,
                SeatStatusEnum.LOCKED,
            ],
            row_prefix='S',
        )

        all_results = recommend_events()
        result_ids = {
            result['event_id']
            for result in all_results
        }

        self.assertIn(eligible_event.id, result_ids)
        self.assertIn(other_valid_event.id, result_ids)
        self.assertNotIn(pending_event.id, result_ids)
        self.assertNotIn(cancelled_event.id, result_ids)
        self.assertNotIn(past_event.id, result_ids)
        self.assertNotIn(sold_out_event.id, result_ids)

        filtered_results = recommend_events(
            category='music',
            location='TP.HCM',
            max_price=Decimal('250000.00'),
            date_from=(now + timedelta(days=6)).date(),
            date_to=(now + timedelta(days=8)).date(),
        )

        self.assertEqual(len(filtered_results), 1)
        self.assertEqual(
            filtered_results[0]['event_id'],
            eligible_event.id,
        )
        self.assertEqual(
            filtered_results[0]['min_ticket_price'],
            Decimal('200000.00'),
        )
        self.assertEqual(
            filtered_results[0]['max_ticket_price'],
            Decimal('500000.00'),
        )
        self.assertEqual(
            filtered_results[0]['available_seats'],
            3,
        )

    def test_recommend_events_returns_at_most_five_events(self):
        for index in range(6):
            event = self.create_event(
                title=f'Event {index}',
                start_time=(
                    timezone.now()
                    + timedelta(days=index + 1)
                ),
            )
            self.create_ticket_type_with_seats(
                event=event,
                name='Vé thường',
                price=Decimal('100000.00'),
                seat_statuses=[SeatStatusEnum.AVAILABLE],
                row_prefix=f'R{index}',
            )

        results = recommend_events()

        self.assertEqual(len(results), 5)
        self.assertEqual(
            [result['title'] for result in results],
            [f'Event {index}' for index in range(5)],
        )

    def test_check_event_availability_counts_each_ticket_type(self):
        event = self.create_event(
            title='Đêm nhạc mùa hè',
        )
        self.create_ticket_type_with_seats(
            event=event,
            name='VIP',
            price=Decimal('500000.00'),
            seat_statuses=[
                SeatStatusEnum.AVAILABLE,
                SeatStatusEnum.AVAILABLE,
                SeatStatusEnum.SOLD,
            ],
            row_prefix='VIP',
        )
        self.create_ticket_type_with_seats(
            event=event,
            name='Thường',
            price=Decimal('200000.00'),
            seat_statuses=[
                SeatStatusEnum.AVAILABLE,
                SeatStatusEnum.LOCKED,
            ],
            row_prefix='A',
        )

        result = check_event_availability(
            event_id=event.id,
        )

        self.assertEqual(result['status'], 'found')
        self.assertEqual(result['event_id'], event.id)
        self.assertEqual(result['available_seats'], 3)
        self.assertEqual(result['total_seats'], 5)

        ticket_results = {
            item['ticket_type_name']: item
            for item in result['ticket_types']
        }

        self.assertEqual(
            ticket_results['VIP']['available_count'],
            2,
        )
        self.assertEqual(
            ticket_results['VIP']['total_count'],
            3,
        )
        self.assertEqual(
            ticket_results['Thường']['available_count'],
            1,
        )
        self.assertEqual(
            ticket_results['Thường']['total_count'],
            2,
        )

    def test_check_event_availability_returns_multiple_suggestions(self):
        first_event = self.create_event(
            title='Đêm nhạc mùa hè',
            start_time=timezone.now() + timedelta(days=5),
        )
        second_event = self.create_event(
            title='Đêm nhạc mùa thu',
            start_time=timezone.now() + timedelta(days=10),
        )

        result = check_event_availability(
            event_name='Đêm nhạc mùa',
        )

        self.assertEqual(
            result['status'],
            'multiple_matches',
        )
        self.assertEqual(result['match_count'], 2)
        self.assertEqual(len(result['suggestions']), 2)
        self.assertEqual(
            {
                suggestion['event_id']
                for suggestion in result['suggestions']
            },
            {first_event.id, second_event.id},
        )

    def test_check_event_availability_returns_not_found(self):
        result = check_event_availability(
            event_name='Sự kiện không tồn tại',
        )

        self.assertEqual(result['status'], 'not_found')
        self.assertEqual(result['suggestions'], [])

        invalid_id_result = check_event_availability(
            event_id='khong-phai-so',
        )

        self.assertEqual(
            invalid_id_result['status'],
            'not_found',
        )

    def test_estimate_event_budget_calculates_exact_amounts(self):
        self.create_service(
            code='CATERING_TEST',
            name='Catering Test',
            category=ServiceCategoryEnum.CATERING,
            pricing_unit=PricingUnitEnum.PER_PERSON,
            min_price=Decimal('100.00'),
            max_price=Decimal('200.00'),
        )
        self.create_service(
            code='SOUND_TEST',
            name='Âm thanh Test',
            category=ServiceCategoryEnum.SOUND_LIGHT,
            pricing_unit=PricingUnitEnum.PACKAGE,
            min_price=Decimal('1000.00'),
            max_price=Decimal('2000.00'),
        )

        result = estimate_event_budget(
            guest_count=10,
            quality_level='standard',
            location='TP.HCM',
            service_categories=[
                'CATERING',
                'SOUND_LIGHT',
            ],
        )

        self.assertEqual(
            result['min_cost'],
            Decimal('2000.00'),
        )
        self.assertEqual(
            result['max_cost'],
            Decimal('4000.00'),
        )
        self.assertEqual(
            result['contingency'],
            Decimal('400.00'),
        )
        self.assertEqual(
            result['total_estimated_cost'],
            Decimal('4400.00'),
        )
        self.assertEqual(len(result['breakdown']), 2)

        breakdown = {
            item['category']: item
            for item in result['breakdown']
        }

        self.assertEqual(
            breakdown['CATERING']['calculated_min_cost'],
            Decimal('1000.00'),
        )
        self.assertEqual(
            breakdown['SOUND_LIGHT']['calculated_min_cost'],
            Decimal('1000.00'),
        )

    def test_estimate_event_budget_validates_input(self):
        with self.assertRaisesMessage(
            ValueError,
            'Số khách phải là số nguyên lớn hơn 0',
        ):
            estimate_event_budget(
                guest_count=0,
                quality_level='STANDARD',
                location='TP.HCM',
                service_categories=['CATERING'],
            )

        with self.assertRaisesMessage(
            ValueError,
            'Không tìm thấy dịch vụ phù hợp',
        ):
            estimate_event_budget(
                guest_count=100,
                quality_level='STANDARD',
                location='Địa điểm không tồn tại',
                service_categories=['CATERING'],
            )

    def test_suggest_ticket_price_calculates_market_reference(self):
        event = self.create_event(
            title='Concert tham khảo',
            category=EventCategoryEnum.MUSIC,
        )
        TicketType.objects.create(
            event=event,
            name='Thường',
            price=Decimal('100.00'),
            quantity=100,
        )
        TicketType.objects.create(
            event=event,
            name='VIP',
            price=Decimal('300.00'),
            quantity=50,
        )

        result = suggest_ticket_price(
            total_estimated_cost=Decimal('1000.00'),
            guest_count=4,
            category='music',
        )

        self.assertEqual(
            result['breakeven_price'],
            Decimal('250.00'),
        )
        self.assertEqual(
            result['market_reference_avg_price'],
            Decimal('200.00'),
        )

    def test_suggest_ticket_price_returns_none_without_market_data(self):
        result = suggest_ticket_price(
            total_estimated_cost=Decimal('1000.00'),
            guest_count=4,
            category=EventCategoryEnum.SPORTS,
        )

        self.assertEqual(
            result['breakeven_price'],
            Decimal('250.00'),
        )
        self.assertIsNone(
            result['market_reference_avg_price']
        )
