from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.db.models import Avg, Count, Max, Min, Q
from django.utils import timezone
from django.utils.dateparse import parse_date

from ai_agent.models import (
    EventService,
    PricingUnitEnum,
    QualityLevelEnum,
    ServiceCategoryEnum,
)
from events.models import (
    Event,
    EventCategoryEnum,
    EventStatusEnum,
    TicketType,
)
from seating.models import SeatStatusEnum


MONEY_QUANTIZER = Decimal('0.01')
CONTINGENCY_RATE = Decimal('0.10')
MAX_RECOMMENDED_EVENTS = 5


def _to_decimal(value, field_name):
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(
            f'{field_name} phải là một số hợp lệ.'
        ) from exc

    if not decimal_value.is_finite():
        raise ValueError(f'{field_name} phải là một số hữu hạn.')

    return decimal_value


def _to_positive_integer(value, field_name):
    decimal_value = _to_decimal(value, field_name)

    if (
        decimal_value <= 0
        or decimal_value != decimal_value.to_integral_value()
    ):
        raise ValueError(f'{field_name} phải là số nguyên lớn hơn 0.')

    return int(decimal_value)


def _normalize_date(value, field_name):
    if value is None or value == '':
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    parsed_value = parse_date(str(value).strip())

    if parsed_value is None:
        raise ValueError(
            f'{field_name} phải có định dạng YYYY-MM-DD.'
        )

    return parsed_value


def _money(value):
    return Decimal(value).quantize(
        MONEY_QUANTIZER,
        rounding=ROUND_HALF_UP,
    )


def recommend_events(
    category=None,
    location=None,
    max_price=None,
    date_from=None,
    date_to=None,
):
    selected_category = None

    if category:
        selected_category = str(category).strip().upper()

        if selected_category not in EventCategoryEnum.values:
            raise ValueError(
                f'Danh mục sự kiện không hợp lệ: {selected_category}.'
            )

    selected_location = str(location or '').strip()
    selected_max_price = None

    if max_price is not None and max_price != '':
        selected_max_price = _to_decimal(
            max_price,
            'Giá vé tối đa',
        )

        if selected_max_price < 0:
            raise ValueError('Giá vé tối đa không được nhỏ hơn 0.')

    selected_date_from = _normalize_date(
        date_from,
        'Ngày bắt đầu',
    )
    selected_date_to = _normalize_date(
        date_to,
        'Ngày kết thúc',
    )

    if (
        selected_date_from
        and selected_date_to
        and selected_date_from > selected_date_to
    ):
        raise ValueError(
            'Ngày bắt đầu không được lớn hơn ngày kết thúc.'
        )

    queryset = (
        Event.objects
        .filter(
            status=EventStatusEnum.PUBLISHED,
            start_time__gt=timezone.now(),
        )
        .annotate(
            min_ticket_price=Min('ticket_types__price'),
            max_ticket_price=Max('ticket_types__price'),
            available_seats=Count(
                'seats',
                filter=Q(
                    seats__status=SeatStatusEnum.AVAILABLE
                ),
                distinct=True,
            ),
        )
        .filter(available_seats__gt=0)
    )

    if selected_category:
        queryset = queryset.filter(category=selected_category)

    if selected_location:
        queryset = queryset.filter(
            location__icontains=selected_location
        )

    if selected_date_from:
        queryset = queryset.filter(
            start_time__date__gte=selected_date_from
        )

    if selected_date_to:
        queryset = queryset.filter(
            start_time__date__lte=selected_date_to
        )

    if selected_max_price is not None:
        queryset = queryset.filter(
            min_ticket_price__lte=selected_max_price
        )

    events = queryset.order_by(
        'start_time',
        'id',
    )[:MAX_RECOMMENDED_EVENTS]

    return [
        {
            'event_id': event.id,
            'title': event.title,
            'thumbnail': event.thumbnail,
            'location': event.location,
            'start_time': event.start_time.isoformat(),
            'category': event.category,
            'min_ticket_price': (
                _money(event.min_ticket_price)
                if event.min_ticket_price is not None
                else None
            ),
            'max_ticket_price': (
                _money(event.max_ticket_price)
                if event.max_ticket_price is not None
                else None
            ),
            'available_seats': event.available_seats,
        }
        for event in events
    ]


def check_event_availability(
    event_id=None,
    event_name=None,
):
    selected_name = str(event_name or '').strip()
    base_queryset = Event.objects.filter(
        status=EventStatusEnum.PUBLISHED,
        start_time__gt=timezone.now(),
    )

    if event_id is not None and event_id != '':
        try:
            selected_event_id = int(event_id)
        except (TypeError, ValueError):
            return {
                'status': 'not_found',
                'message': 'Không tìm thấy sự kiện phù hợp.',
                'suggestions': [],
            }

        event = base_queryset.filter(
            id=selected_event_id
        ).first()

        if event is None:
            return {
                'status': 'not_found',
                'message': 'Không tìm thấy sự kiện phù hợp.',
                'suggestions': [],
            }
    else:
        if not selected_name:
            raise ValueError(
                'Cần cung cấp event_id hoặc event_name.'
            )

        matched_events = (
            base_queryset
            .filter(title__icontains=selected_name)
            .order_by('start_time', 'id')
        )
        match_count = matched_events.count()

        if match_count == 0:
            return {
                'status': 'not_found',
                'message': 'Không tìm thấy sự kiện phù hợp.',
                'suggestions': [],
            }

        if match_count > 1:
            suggestions = [
                {
                    'event_id': matched_event.id,
                    'title': matched_event.title,
                    'location': matched_event.location,
                    'start_time': (
                        matched_event.start_time.isoformat()
                    ),
                }
                for matched_event in matched_events[
                    :MAX_RECOMMENDED_EVENTS
                ]
            ]

            return {
                'status': 'multiple_matches',
                'message': (
                    'Có nhiều sự kiện trùng với tên tìm kiếm. '
                    'Vui lòng chọn một sự kiện cụ thể.'
                ),
                'match_count': match_count,
                'suggestions': suggestions,
            }

        event = matched_events.first()

    ticket_types = (
        event.ticket_types
        .annotate(
            available_count=Count(
                'seats',
                filter=Q(
                    seats__status=SeatStatusEnum.AVAILABLE
                ),
            ),
            total_count=Count('seats'),
        )
        .order_by('price', 'id')
    )

    ticket_type_results = [
        {
            'ticket_type_id': ticket_type.id,
            'ticket_type_name': ticket_type.name,
            'price': _money(ticket_type.price),
            'available_count': ticket_type.available_count,
            'total_count': ticket_type.total_count,
        }
        for ticket_type in ticket_types
    ]

    return {
        'status': 'found',
        'message': 'Đã tìm thấy thông tin ghế của sự kiện.',
        'event_id': event.id,
        'title': event.title,
        'thumbnail': event.thumbnail,
        'location': event.location,
        'start_time': event.start_time.isoformat(),
        'available_seats': sum(
            ticket_type['available_count']
            for ticket_type in ticket_type_results
        ),
        'total_seats': sum(
            ticket_type['total_count']
            for ticket_type in ticket_type_results
        ),
        'ticket_types': ticket_type_results,
    }


def estimate_event_budget(
    guest_count,
    quality_level,
    location,
    service_categories,
    duration_hours=None,
):
    selected_guest_count = _to_positive_integer(
        guest_count,
        'Số khách',
    )
    selected_quality = str(quality_level or '').strip().upper()
    selected_location = str(location or '').strip()

    if selected_quality not in QualityLevelEnum.values:
        raise ValueError(
            f'Mức chất lượng không hợp lệ: {selected_quality}.'
        )

    if not selected_location:
        raise ValueError('Địa điểm không được để trống.')

    if not isinstance(service_categories, (list, tuple)):
        raise ValueError(
            'Danh mục dịch vụ phải là một danh sách.'
        )

    selected_categories = []

    for category in service_categories:
        selected_category = str(category).strip().upper()

        if selected_category not in ServiceCategoryEnum.values:
            raise ValueError(
                f'Danh mục dịch vụ không hợp lệ: '
                f'{selected_category}.'
            )

        if selected_category not in selected_categories:
            selected_categories.append(selected_category)

    if not selected_categories:
        raise ValueError(
            'Cần chọn ít nhất một danh mục dịch vụ.'
        )

    selected_duration = None

    if duration_hours is not None and duration_hours != '':
        selected_duration = _to_decimal(
            duration_hours,
            'Thời lượng',
        )

        if selected_duration <= 0:
            raise ValueError(
                'Thời lượng phải lớn hơn 0 giờ.'
            )

    matching_services = list(
        EventService.objects
        .filter(
            is_active=True,
            quality_level=selected_quality,
            location__icontains=selected_location,
            category__in=selected_categories,
            min_capacity__lte=selected_guest_count,
            max_capacity__gte=selected_guest_count,
        )
        .order_by(
            'category',
            'max_price',
            'min_price',
            'id',
        )
    )

    services_by_category = {}

    for service in matching_services:
        if service.category not in services_by_category:
            services_by_category[service.category] = service

    missing_categories = [
        category
        for category in selected_categories
        if category not in services_by_category
    ]

    if missing_categories:
        raise ValueError(
            'Không tìm thấy dịch vụ phù hợp cho: '
            + ', '.join(missing_categories)
            + '. Vui lòng kiểm tra lại địa điểm, '
            'mức chất lượng hoặc số khách.'
        )

    min_cost = Decimal('0.00')
    max_cost = Decimal('0.00')
    breakdown = []

    for category in selected_categories:
        service = services_by_category[category]
        quantity = Decimal('1')

        if service.pricing_unit == PricingUnitEnum.PER_PERSON:
            quantity = Decimal(selected_guest_count)

        elif service.pricing_unit == PricingUnitEnum.PER_HOUR:
            hours = selected_duration

            if hours is None and service.included_duration_hours:
                hours = Decimal(service.included_duration_hours)

            if hours is None:
                raise ValueError(
                    f'Dịch vụ {service.name} tính theo giờ. '
                    'Cần cung cấp duration_hours.'
                )

            quantity = hours

        service_min_cost = _money(
            service.min_price * quantity
        )
        service_max_cost = _money(
            service.max_price * quantity
        )

        min_cost += service_min_cost
        max_cost += service_max_cost

        breakdown.append({
            'service_id': service.id,
            'code': service.code,
            'name': service.name,
            'provider_name': service.provider_name,
            'category': service.category,
            'quality_level': service.quality_level,
            'location': service.location,
            'pricing_unit': service.pricing_unit,
            'unit_min_price': _money(service.min_price),
            'unit_max_price': _money(service.max_price),
            'quantity': quantity,
            'calculated_min_cost': service_min_cost,
            'calculated_max_cost': service_max_cost,
            'verified_at': service.verified_at.isoformat(),
        })

    min_cost = _money(min_cost)
    max_cost = _money(max_cost)
    contingency = _money(
        max_cost * CONTINGENCY_RATE
    )
    total_estimated_cost = _money(
        max_cost + contingency
    )

    return {
        'guest_count': selected_guest_count,
        'quality_level': selected_quality,
        'location': selected_location,
        'min_cost': min_cost,
        'max_cost': max_cost,
        'contingency_rate': CONTINGENCY_RATE,
        'contingency': contingency,
        'total_estimated_cost': total_estimated_cost,
        'breakdown': breakdown,
    }


def suggest_ticket_price(
    total_estimated_cost,
    guest_count,
    category,
):
    selected_total_cost = _to_decimal(
        total_estimated_cost,
        'Tổng chi phí dự kiến',
    )
    selected_guest_count = _to_positive_integer(
        guest_count,
        'Số vé dự kiến bán',
    )
    selected_category = str(category or '').strip().upper()

    if selected_total_cost <= 0:
        raise ValueError(
            'Tổng chi phí dự kiến phải lớn hơn 0.'
        )

    if selected_category not in EventCategoryEnum.values:
        raise ValueError(
            f'Danh mục sự kiện không hợp lệ: '
            f'{selected_category}.'
        )

    breakeven_price = _money(
        selected_total_cost
        / Decimal(selected_guest_count)
    )

    market_average = (
        TicketType.objects
        .filter(
            event__status=EventStatusEnum.PUBLISHED,
            event__category=selected_category,
        )
        .aggregate(average_price=Avg('price'))
        .get('average_price')
    )

    return {
        'total_estimated_cost': _money(
            selected_total_cost
        ),
        'expected_ticket_sales': selected_guest_count,
        'category': selected_category,
        'breakeven_price': breakeven_price,
        'market_reference_avg_price': (
            _money(market_average)
            if market_average is not None
            else None
        ),
    }
