from datetime import datetime, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.utils import timezone

from authentication.models import (
    Customer,
    CustomerTierEnum,
    Organizer,
    User,
    UserType,
)
from events.models import (
    Event,
    EventCategoryEnum,
    EventStatusEnum,
    TicketType,
)
from orders.models import (
    Order,
    OrderItem,
    OrderStatusEnum,
    Payment,
    PaymentStatusEnum,
    Ticket,
)
from seating.models import Seat, SeatStatusEnum


DEMO_DATABASE_NAME = 'smart_booking_report_demo'
DEMO_USER_PREFIX = 'report_demo_'
DEMO_EVENT_PREFIX = '[DEMO REPORT]'

ADMIN_PASSWORD = 'DemoAdmin@123'
ORGANIZER_PASSWORD = 'DemoOrganizer@123'
CUSTOMER_PASSWORD = 'DemoCustomer@123'


ORGANIZER_DATA = [
    ('Sắc Màu Events', '190000000001 - Vietcombank'),
    ('Mây Trắng Entertainment', '190000000002 - Techcombank'),
    ('Nova Workshop', '190000000003 - MB Bank'),
    ('Năng Động Sports', '190000000004 - VietinBank'),
]


EVENT_DATA = [
    {
        'title': 'Summer Music Festival',
        'category': EventCategoryEnum.MUSIC,
        'organizer_index': 0,
        'location': 'Nhà thi đấu Phú Thọ, TP.HCM',
        'standard_price': Decimal('350000'),
        'vip_price': Decimal('850000'),
        'thumbnail': 'https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=900',
    },
    {
        'title': 'Acoustic Night Sài Gòn',
        'category': EventCategoryEnum.MUSIC,
        'organizer_index': 1,
        'location': 'Nhà hát Hòa Bình, TP.HCM',
        'standard_price': Decimal('250000'),
        'vip_price': Decimal('550000'),
        'thumbnail': 'https://images.unsplash.com/photo-1516280440614-37939bbacd81?w=900',
    },
    {
        'title': 'AI For Business Workshop',
        'category': EventCategoryEnum.WORKSHOP,
        'organizer_index': 2,
        'location': 'GEM Center, TP.HCM',
        'standard_price': Decimal('180000'),
        'vip_price': Decimal('420000'),
        'thumbnail': 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=900',
    },
    {
        'title': 'Startup Growth Conference',
        'category': EventCategoryEnum.WORKSHOP,
        'organizer_index': 2,
        'location': 'Thiskyhall Sala, TP.HCM',
        'standard_price': Decimal('220000'),
        'vip_price': Decimal('480000'),
        'thumbnail': 'https://images.unsplash.com/photo-1505373877841-8d25f7d46678?w=900',
    },
    {
        'title': 'Comedy Weekend Show',
        'category': EventCategoryEnum.ENTERTAINMENT,
        'organizer_index': 1,
        'location': 'Sân khấu IDECAF, TP.HCM',
        'standard_price': Decimal('200000'),
        'vip_price': Decimal('450000'),
        'thumbnail': 'https://images.unsplash.com/photo-1527224857830-43a7acc85260?w=900',
    },
    {
        'title': 'Contemporary Art Experience',
        'category': EventCategoryEnum.ENTERTAINMENT,
        'organizer_index': 0,
        'location': 'SECC, Quận 7, TP.HCM',
        'standard_price': Decimal('150000'),
        'vip_price': Decimal('300000'),
        'thumbnail': 'https://images.unsplash.com/photo-1549490349-8643362247b5?w=900',
    },
    {
        'title': 'Saigon Night Marathon',
        'category': EventCategoryEnum.SPORTS,
        'organizer_index': 3,
        'location': 'Công viên Tao Đàn, TP.HCM',
        'standard_price': Decimal('300000'),
        'vip_price': Decimal('600000'),
        'thumbnail': 'https://images.unsplash.com/photo-1552674605-db6ffd4facb5?w=900',
    },
    {
        'title': 'City Basketball Final',
        'category': EventCategoryEnum.SPORTS,
        'organizer_index': 3,
        'location': 'Nhà thi đấu Hồ Xuân Hương, TP.HCM',
        'standard_price': Decimal('180000'),
        'vip_price': Decimal('380000'),
        'thumbnail': 'https://images.unsplash.com/photo-1546519638-68e109498ffc?w=900',
    },
]


class Command(BaseCommand):
    help = 'Tạo hoặc xóa dữ liệu trình diễn cho báo cáo doanh thu Admin.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Chỉ xóa dữ liệu demo do command này tạo.',
        )

    def handle(self, *args, **options):
        self.ensure_demo_database()

        if options['clear']:
            with transaction.atomic():
                deleted_count = self.clear_demo_data()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Đã xóa {deleted_count} bản ghi thuộc bộ dữ liệu demo.'
                )
            )
            return

        if self.demo_data_exists():
            raise CommandError(
                'Dữ liệu demo đã tồn tại. Hãy chạy '
                '"python seed_admin_report_demo.py --clear" trước.'
            )

        with transaction.atomic():
            self.create_demo_admin()
            organizers = self.create_demo_organizers()
            customers = self.create_demo_customers()
            events = self.create_demo_events(organizers)
            result = self.create_demo_orders(events, customers)

        self.print_result(result)

    def ensure_demo_database(self):
        database_name = str(connection.settings_dict.get('NAME', ''))
        if database_name.lower() != DEMO_DATABASE_NAME:
            raise CommandError(
                f'Command chỉ được chạy trên database "{DEMO_DATABASE_NAME}". '
                f'Database hiện tại là "{database_name}".'
            )

        self.stdout.write(f'Database đang sử dụng: {database_name}')

    def demo_data_exists(self):
        return (
            User.objects.filter(
                username__startswith=DEMO_USER_PREFIX,
            ).exists()
            or Event.objects.filter(
                title__startswith=DEMO_EVENT_PREFIX,
            ).exists()
        )

    def clear_demo_data(self):
        event_deleted_count, _ = Event.objects.filter(
            title__startswith=DEMO_EVENT_PREFIX,
        ).delete()
        user_deleted_count, _ = User.objects.filter(
            username__startswith=DEMO_USER_PREFIX,
        ).delete()
        return event_deleted_count + user_deleted_count

    def create_demo_admin(self):
        User.objects.create_user(
            username='report_demo_admin',
            email='report.demo.admin@smartticket.test',
            phone_number='0888800000',
            name='Admin Báo Cáo Demo',
            type=UserType.ADMIN,
            status=True,
            is_active=True,
            is_staff=True,
            is_superuser=True,
            password=ADMIN_PASSWORD,
        )

    def create_demo_organizers(self):
        organizers = []

        for index, (company_name, bank_account) in enumerate(
            ORGANIZER_DATA,
            start=1,
        ):
            user = User.objects.create_user(
                username=f'report_demo_organizer_{index}',
                email=f'report.demo.organizer{index}@smartticket.test',
                phone_number=f'08888100{index:02d}',
                name=f'Ban Tổ Chức Demo {index}',
                type=UserType.ORGANIZER,
                status=True,
                is_active=True,
                password=ORGANIZER_PASSWORD,
            )
            organizers.append(
                Organizer.objects.create(
                    user=user,
                    company_name=company_name,
                    bank_account=bank_account,
                )
            )

        return organizers

    def create_demo_customers(self):
        customers = []
        tiers = list(CustomerTierEnum.values)

        for index in range(1, 13):
            user = User.objects.create_user(
                username=f'report_demo_customer_{index}',
                email=f'report.demo.customer{index}@smartticket.test',
                phone_number=f'08888200{index:02d}',
                name=f'Khách Hàng Demo {index}',
                type=UserType.CUSTOMER,
                status=True,
                is_active=True,
                password=CUSTOMER_PASSWORD,
            )
            customers.append(
                Customer.objects.create(
                    user=user,
                    tier=tiers[(index - 1) % len(tiers)],
                )
            )

        return customers

    def create_demo_events(self, organizers):
        events = []
        now = timezone.now()
        created_at = self.get_month_datetime(7, 2)

        for index, data in enumerate(EVENT_DATA):
            event = Event.objects.create(
                organizer=organizers[data['organizer_index']],
                title=f'{DEMO_EVENT_PREFIX} {data["title"]}',
                thumbnail=data['thumbnail'],
                description=(
                    'Sự kiện mẫu dùng để trình diễn báo cáo doanh thu, '
                    'giao dịch, vé và quyết toán trong đồ án SmartTicket.'
                ),
                location=data['location'],
                start_time=now - timedelta(days=8 - index),
                category=data['category'],
                status=EventStatusEnum.PUBLISHED,
                is_payout_completed=index < 3,
            )
            Event.objects.filter(id=event.id).update(
                created_at=created_at,
                updated_at=created_at,
            )

            standard_type = TicketType.objects.create(
                event=event,
                name='Phổ thông',
                price=data['standard_price'],
                quantity=25,
            )
            vip_type = TicketType.objects.create(
                event=event,
                name='VIP',
                price=data['vip_price'],
                quantity=25,
            )

            Seat.objects.bulk_create([
                Seat(
                    event=event,
                    ticket_type=standard_type,
                    row='STD',
                    number=number,
                    seat_name=f'STD-{number}',
                )
                for number in range(1, 26)
            ])
            Seat.objects.bulk_create([
                Seat(
                    event=event,
                    ticket_type=vip_type,
                    row='VIP',
                    number=number,
                    seat_name=f'VIP-{number}',
                )
                for number in range(1, 26)
            ])

            events.append({
                'event': event,
                'ticket_types': [standard_type, vip_type],
                'seats': {
                    standard_type.id: list(
                        Seat.objects.filter(
                            ticket_type=standard_type,
                        ).order_by('number')
                    ),
                    vip_type.id: list(
                        Seat.objects.filter(
                            ticket_type=vip_type,
                        ).order_by('number')
                    ),
                },
            })

        return events

    def create_demo_orders(self, events, customers):
        seat_positions = {
            ticket_type.id: 0
            for event_data in events
            for ticket_type in event_data['ticket_types']
        }
        sold_seat_ids = []
        order_count = 0
        ticket_count = 0
        checked_in_count = 0
        total_revenue = Decimal('0.00')

        for month_position in range(6):
            months_ago = 6 - month_position

            for order_in_month in range(10):
                event_data = events[
                    (month_position * 3 + order_in_month) % len(events)
                ]
                event = event_data['event']
                customer = customers[order_count % len(customers)]
                seats_in_order = 1 + (order_count % 3)
                selected_seats = []

                for position in range(seats_in_order):
                    ticket_type = event_data['ticket_types'][
                        (order_count + position) % 2
                    ]
                    seat_index = seat_positions[ticket_type.id]
                    seat = event_data['seats'][ticket_type.id][seat_index]
                    seat_positions[ticket_type.id] += 1
                    selected_seats.append((seat, ticket_type))

                total_amount = sum(
                    (ticket_type.price for _, ticket_type in selected_seats),
                    Decimal('0.00'),
                )
                order_date = self.get_month_datetime(
                    months_ago,
                    5 + order_in_month,
                )
                payment_date = order_date + timedelta(minutes=2)

                order = Order.objects.create(
                    customer=customer,
                    event=event,
                    total_amount=total_amount,
                    status=OrderStatusEnum.PAID,
                    expires_at=order_date + timedelta(minutes=10),
                )
                Order.objects.filter(id=order.id).update(
                    created_at=order_date,
                    updated_at=payment_date,
                )

                for seat, ticket_type in selected_seats:
                    order_item = OrderItem.objects.create(
                        order=order,
                        seat=seat,
                        ticket_type=ticket_type,
                        unit_price=ticket_type.price,
                    )
                    OrderItem.objects.filter(id=order_item.id).update(
                        created_at=order_date,
                    )

                    is_checked_in = ticket_count % 5 < 3
                    checked_in_at = None
                    if is_checked_in:
                        checked_in_at = event.start_time + timedelta(hours=2)
                        checked_in_count += 1

                    Ticket.objects.create(
                        order=order,
                        seat=seat,
                        ticket_type=ticket_type,
                        qr_code=(
                            f'DEMO-REPORT-TICKET-{order.id}-{seat.id}'
                        ),
                        is_checked_in=is_checked_in,
                        issued_at=payment_date,
                        checked_in_at=checked_in_at,
                    )
                    sold_seat_ids.append(seat.id)
                    ticket_count += 1

                payment = Payment.objects.create(
                    order=order,
                    provider='PAYOS-DEMO',
                    transaction_id=f'DEMO-REPORT-{order.id:06d}',
                    amount=total_amount,
                    status=PaymentStatusEnum.SUCCESS,
                )
                Payment.objects.filter(id=payment.id).update(
                    created_at=payment_date,
                    updated_at=payment_date,
                )

                order_count += 1
                total_revenue += total_amount

        Seat.objects.filter(id__in=sold_seat_ids).update(
            status=SeatStatusEnum.SOLD,
            locked_until=None,
            locked_by_order=None,
        )

        return {
            'organizer_count': len(ORGANIZER_DATA),
            'customer_count': len(customers),
            'event_count': len(events),
            'order_count': order_count,
            'ticket_count': ticket_count,
            'checked_in_count': checked_in_count,
            'total_revenue': total_revenue,
        }

    def get_month_datetime(self, months_ago, day):
        today = timezone.localdate()
        month_number = today.year * 12 + today.month - 1 - months_ago
        year, month_index = divmod(month_number, 12)
        naive_datetime = datetime(year, month_index + 1, day, 10, 0)
        return timezone.make_aware(
            naive_datetime,
            timezone.get_current_timezone(),
        )

    def print_result(self, result):
        formatted_revenue = (
            f'{result["total_revenue"]:,.0f}'.replace(',', '.')
        )
        self.stdout.write(self.style.SUCCESS('Đã tạo dữ liệu báo cáo demo.'))
        self.stdout.write(
            f'- {result["organizer_count"]} ban tổ chức'
        )
        self.stdout.write(f'- {result["customer_count"]} khách hàng')
        self.stdout.write(f'- {result["event_count"]} sự kiện')
        self.stdout.write(f'- {result["order_count"]} đơn PAID')
        self.stdout.write(f'- {result["ticket_count"]} vé đã bán')
        self.stdout.write(
            f'- {result["checked_in_count"]} vé đã check-in'
        )
        self.stdout.write(f'- Tổng doanh thu: {formatted_revenue} VNĐ')
        self.stdout.write('')
        self.stdout.write('Tài khoản Admin:')
        self.stdout.write('  report.demo.admin@smartticket.test')
        self.stdout.write(f'  Mật khẩu: {ADMIN_PASSWORD}')
        self.stdout.write('')
        self.stdout.write('Tài khoản Organizer 1:')
        self.stdout.write('  report.demo.organizer1@smartticket.test')
        self.stdout.write(f'  Mật khẩu: {ORGANIZER_PASSWORD}')
        self.stdout.write('')
        self.stdout.write('Tài khoản Customer 1:')
        self.stdout.write('  report.demo.customer1@smartticket.test')
        self.stdout.write(f'  Mật khẩu: {CUSTOMER_PASSWORD}')
