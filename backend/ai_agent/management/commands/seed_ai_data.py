import json
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ai_agent.models import (
    EventService,
    PricingUnitEnum,
    QualityLevelEnum,
    ServiceCategoryEnum,
)


DATA_FILE = Path(settings.BASE_DIR) / 'ai_agent' / 'data' / 'event_services.json'


class Command(BaseCommand):
    help = 'Nạp dữ liệu dịch vụ sự kiện mẫu vào database.'

    def handle(self, *args, **options):
        payload = self._read_json_file()
        raw_services = payload.get('services')

        if not isinstance(raw_services, list) or not raw_services:
            raise CommandError('File JSON phải có danh sách services không rỗng.')

        services = []
        service_codes = set()

        for index, raw_service in enumerate(raw_services, start=1):
            service = self._validate_service(raw_service, index)

            if service['code'] in service_codes:
                raise CommandError(
                    f'Mã dịch vụ bị trùng: {service["code"]}.'
                )

            service_codes.add(service['code'])
            services.append(service)

        created_count = 0
        updated_count = 0

        with transaction.atomic():
            for service in services:
                code = service.pop('code')
                _, created = EventService.objects.update_or_create(
                    code=code,
                    defaults=service,
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Đã xử lý {len(services)} dịch vụ: '
            f'tạo mới {created_count}, cập nhật {updated_count}.'
        ))

    def _read_json_file(self):
        if not DATA_FILE.exists():
            raise CommandError(f'Không tìm thấy file dữ liệu: {DATA_FILE}')

        try:
            with DATA_FILE.open('r', encoding='utf-8') as file:
                payload = json.load(file)
        except json.JSONDecodeError as exc:
            raise CommandError(
                f'File event_services.json không hợp lệ: {exc}'
            ) from exc

        if not isinstance(payload, dict):
            raise CommandError('Nội dung JSON phải là một object.')

        return payload

    def _validate_service(self, raw_service, index):
        if not isinstance(raw_service, dict):
            raise CommandError(f'Dịch vụ thứ {index} phải là một object.')

        required_fields = [
            'code', 'name', 'provider_name', 'category', 'quality_level',
            'location', 'pricing_unit', 'min_price', 'max_price',
            'min_capacity', 'max_capacity', 'included_duration_hours',
            'description', 'source_url', 'verified_at', 'is_active',
        ]
        missing_fields = [
            field for field in required_fields if field not in raw_service
        ]

        if missing_fields:
            raise CommandError(
                f'Dịch vụ thứ {index} thiếu field: '
                f'{", ".join(missing_fields)}.'
            )

        code = str(raw_service['code']).strip().upper()
        name = str(raw_service['name']).strip()
        provider_name = str(raw_service['provider_name']).strip()
        location = str(raw_service['location']).strip()
        description = str(raw_service['description']).strip()

        if not all([code, name, provider_name, location, description]):
            raise CommandError(
                f'Dịch vụ thứ {index} có nội dung bắt buộc bị trống.'
            )

        category = str(raw_service['category']).strip().upper()
        quality_level = str(raw_service['quality_level']).strip().upper()
        pricing_unit = str(raw_service['pricing_unit']).strip().upper()

        if category not in ServiceCategoryEnum.values:
            raise CommandError(f'Category không hợp lệ ở dịch vụ {code}.')

        if quality_level not in QualityLevelEnum.values:
            raise CommandError(
                f'Quality level không hợp lệ ở dịch vụ {code}.'
            )

        if pricing_unit not in PricingUnitEnum.values:
            raise CommandError(
                f'Pricing unit không hợp lệ ở dịch vụ {code}.'
            )

        try:
            min_price = Decimal(str(raw_service['min_price']))
            max_price = Decimal(str(raw_service['max_price']))
            min_capacity = int(raw_service['min_capacity'])
            max_capacity = int(raw_service['max_capacity'])
            verified_at = date.fromisoformat(str(raw_service['verified_at']))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise CommandError(
                f'Giá, sức chứa hoặc ngày kiểm chứng không hợp lệ ở {code}.'
            ) from exc

        if min_price < 0 or max_price < min_price:
            raise CommandError(f'Khoảng giá không hợp lệ ở dịch vụ {code}.')

        if min_capacity <= 0 or max_capacity < min_capacity:
            raise CommandError(
                f'Khoảng sức chứa không hợp lệ ở dịch vụ {code}.'
            )

        duration = raw_service['included_duration_hours']
        if duration is not None:
            try:
                duration = int(duration)
            except (TypeError, ValueError) as exc:
                raise CommandError(
                    f'Thời lượng không hợp lệ ở dịch vụ {code}.'
                ) from exc

            if duration <= 0:
                raise CommandError(
                    f'Thời lượng phải lớn hơn 0 ở dịch vụ {code}.'
                )

        if not isinstance(raw_service['is_active'], bool):
            raise CommandError(
                f'is_active phải là true hoặc false ở dịch vụ {code}.'
            )

        return {
            'code': code,
            'name': name,
            'provider_name': provider_name,
            'category': category,
            'quality_level': quality_level,
            'location': location,
            'pricing_unit': pricing_unit,
            'min_price': min_price,
            'max_price': max_price,
            'min_capacity': min_capacity,
            'max_capacity': max_capacity,
            'included_duration_hours': duration,
            'description': description,
            'source_url': str(raw_service['source_url']).strip(),
            'verified_at': verified_at,
            'is_active': raw_service['is_active'],
        }
