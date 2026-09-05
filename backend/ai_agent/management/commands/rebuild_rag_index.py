import sys

from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from ai_agent.rag_engine.rag_indexer import rebuild_rag_index


class Command(BaseCommand):
    help = 'Đọc tài liệu Markdown và tạo lại vector index cho RAG.'

    def handle(self, *args, **options):
        # Command Prompt Windows cần UTF-8 để in tiếng Việt.
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')

        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')

        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT current_database()')
                database_name = cursor.fetchone()[0]

            self.stdout.write(
                f'Database đích: {database_name} '
                f'| Host: {connection.settings_dict["HOST"]}'
            )
            self.stdout.write(
                'Bắt đầu tạo embedding từng đoạn, nghỉ 2 giây giữa các đoạn. '
                'Nếu gặp 429, lệnh sẽ tự chờ và thử lại tối đa 3 lần.'
            )

            result = rebuild_rag_index(
                progress_callback=self.stdout.write,
            )
        except Exception as exc:
            raise CommandError(
                f'Đã xảy ra lỗi khi tạo lại RAG index: {exc}'
            ) from exc

        self.stdout.write(self.style.SUCCESS(
            'Tạo RAG index thành công:\n'
            f'- Tài liệu đã xử lý: {result["documents"]}\n'
            f'- Chunk đã tạo: {result["chunks"]}\n'
            f'- Tài liệu tạo mới: {result["created_documents"]}\n'
            f'- Tài liệu cập nhật: {result["updated_documents"]}\n'
            f'- Tài liệu cũ đã xóa: {result["deleted_documents"]}'
        ))
