import sys

from django.core.management.base import BaseCommand, CommandError

from ai_agent.rag_engine.rag_indexer import rebuild_rag_index


class Command(BaseCommand):
    help = 'Đọc tài liệu Markdown và tạo lại vector index cho RAG.'

    def handle(self, *args, **options):
        # Command Prompt Windows cần UTF-8 để in tiếng Việt.
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')

        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')

        self.stdout.write('Bắt đầu đọc tài liệu và tạo embedding...')

        try:
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
