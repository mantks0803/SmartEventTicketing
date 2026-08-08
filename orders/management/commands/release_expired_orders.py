from django.core.management.base import BaseCommand

from orders.services import expire_stale_orders


class Command(BaseCommand):
    help = 'Chuyển đơn PENDING hết hạn thành EXPIRED và nhả các ghế đang giữ.'

    def handle(self, *args, **options):
        expired_count = expire_stale_orders()
        self.stdout.write(
            self.style.SUCCESS(f'Đã xử lý {expired_count} đơn hàng hết hạn.')
        )
