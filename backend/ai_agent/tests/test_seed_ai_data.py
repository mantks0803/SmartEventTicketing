import json
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from ai_agent.models import EventService


class SeedAiDataTests(TestCase):
    def test_seed_command_creates_services_without_duplicates(self):
        # Act: nạp file thật hai lần để kiểm tra update_or_create.
        first_output = StringIO()
        call_command('seed_ai_data', stdout=first_output)
        first_count = EventService.objects.count()

        second_output = StringIO()
        call_command('seed_ai_data', stdout=second_output)

        # Assert: đủ 18 dịch vụ và không bị nhân đôi khi chạy lại.
        self.assertEqual(first_count, 18)
        self.assertEqual(EventService.objects.count(), 18)

        standard_sound = EventService.objects.get(
            code='SOUND_LIGHT_STANDARD'
        )
        self.assertEqual(standard_sound.quality_level, 'STANDARD')
        self.assertEqual(standard_sound.min_price, 15000000)
        self.assertEqual(standard_sound.max_capacity, 600)

    def test_seed_command_rejects_invalid_price_range(self):
        invalid_data = {
            'services': [
                {
                    'code': 'INVALID_PRICE',
                    'name': 'Dịch vụ lỗi',
                    'provider_name': 'Nhà cung cấp minh họa',
                    'category': 'VENUE',
                    'quality_level': 'STANDARD',
                    'location': 'TP.HCM',
                    'pricing_unit': 'PACKAGE',
                    'min_price': 20000000,
                    'max_price': 10000000,
                    'min_capacity': 10,
                    'max_capacity': 100,
                    'included_duration_hours': 4,
                    'description': 'Dữ liệu dùng để kiểm tra validation.',
                    'source_url': '',
                    'verified_at': '2026-08-17',
                    'is_active': True,
                }
            ]
        }

        with TemporaryDirectory() as temporary_directory:
            invalid_file = Path(temporary_directory) / 'invalid.json'
            invalid_file.write_text(
                json.dumps(invalid_data, ensure_ascii=False),
                encoding='utf-8',
            )

            with patch(
                'ai_agent.management.commands.seed_ai_data.DATA_FILE',
                invalid_file,
            ):
                with self.assertRaises(CommandError):
                    call_command('seed_ai_data')

        self.assertEqual(EventService.objects.count(), 0)
