import os
import sys
from pathlib import Path

from django.core.management import execute_from_command_line


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    execute_from_command_line([
        'manage.py',
        'seed_admin_report_demo',
        *sys.argv[1:],
    ])
