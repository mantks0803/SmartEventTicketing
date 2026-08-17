from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import TestCase, override_settings

from ai_agent.models import (
    EMBEDDING_DIMENSIONS,
    KnowledgeAudienceEnum,
    KnowledgeBase,
    KnowledgeChunk,
)
from ai_agent.rag_engine.rag_indexer import (
    CHUNK_SIZE,
    load_markdown_documents,
    rebuild_rag_index,
    search_knowledge,
    split_document,
)


class FakeEmbeddingModel:
    """
    Model embedding giả dùng trong test.

    Test không gọi Gemini thật nên không cần Internet hoặc API key.
    """

    def create_vector(self, text):
        text = text.lower()
        vector = [0.0] * EMBEDDING_DIMENSIONS

        if 'thanh toán' in text or 'payos' in text:
            vector[0] = 1.0
        elif 'ngân sách' in text or 'chi phí' in text:
            vector[1] = 1.0
        else:
            vector[2] = 1.0

        return vector

    def embed_documents(self, texts):
        return [
            self.create_vector(text)
            for text in texts
        ]

    def embed_query(self, text):
        return self.create_vector(text)


class InvalidEmbeddingModel:
    """Model giả trả vector sai số chiều."""

    def embed_documents(self, texts):
        return [
            [1.0, 0.0, 0.0]
            for _ in texts
        ]

    def embed_query(self, text):
        return [1.0, 0.0, 0.0]


@override_settings(
    AI_EMBEDDING_DIMENSIONS=EMBEDDING_DIMENSIONS,
    AI_MAX_CONTEXT_CHUNKS=4,
)
class RagIndexerTests(TestCase):
    def setUp(self):
        # Arrange: tạo thư mục tài liệu tạm cho từng test.
        self.temporary_directory = TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)

        self.knowledge_directory = Path(
            self.temporary_directory.name
        )

        self.write_markdown_file(
            folder_name='customer',
            file_name='01_payment.md',
            title='Hướng dẫn thanh toán PayOS',
            category='POLICY',
            body=(
                'Khách hàng thanh toán đơn hàng qua PayOS. '
                'Sau khi PayOS xác nhận thành công, hệ thống '
                'phát hành vé điện tử cho khách hàng.'
            ),
        )

        self.write_markdown_file(
            folder_name='organizer',
            file_name='01_budget.md',
            title='Lập ngân sách sự kiện',
            category='PLANNING',
            body=(
                'Ban tổ chức cần tính chi phí địa điểm, '
                'âm thanh, ánh sáng và khoản dự phòng.'
            ),
        )

    def write_markdown_file(
        self,
        folder_name,
        file_name,
        title,
        category,
        body,
    ):
        folder = self.knowledge_directory / folder_name
        folder.mkdir(parents=True, exist_ok=True)

        audience = (
            'Customer'
            if folder_name == 'customer'
            else 'Organizer'
        )

        content = (
            f'# {title}\n\n'
            f'> Đối tượng: {audience}\n'
            f'> Danh mục kiến thức: {category}\n\n'
            f'## Nội dung\n\n'
            f'{body}\n'
        )

        (folder / file_name).write_text(
            content,
            encoding='utf-8',
        )

    def test_loader_reads_markdown_metadata(self):
        # Act: đọc hai tài liệu trong thư mục tạm.
        documents = load_markdown_documents(
            self.knowledge_directory
        )

        # Assert: loader đọc đúng tiêu đề, category và audience.
        self.assertEqual(len(documents), 2)

        payment_document = next(
            document
            for document in documents
            if document['source_path'] == 'customer/01_payment.md'
        )

        self.assertEqual(
            payment_document['title'],
            'Hướng dẫn thanh toán PayOS',
        )
        self.assertEqual(
            payment_document['category'],
            'POLICY',
        )
        self.assertEqual(
            payment_document['audience'],
            KnowledgeAudienceEnum.CUSTOMER,
        )

    def test_split_document_creates_small_chunks(self):
        # Arrange: tạo nội dung dài hơn CHUNK_SIZE.
        long_content = ' '.join(
            [
                'Hướng dẫn tổ chức sự kiện và lập ngân sách.'
                for _ in range(100)
            ]
        )

        # Act.
        chunks = split_document(long_content)

        # Assert.
        self.assertGreater(len(chunks), 1)

        for chunk in chunks:
            self.assertLessEqual(len(chunk), CHUNK_SIZE)

    def test_rebuild_is_idempotent_and_search_returns_relevant_document(self):
        fake_model = FakeEmbeddingModel()

        # Act lần 1: tạo dữ liệu KnowledgeBase và KnowledgeChunk.
        first_result = rebuild_rag_index(
            embedding_model=fake_model,
            knowledge_directory=self.knowledge_directory,
        )

        first_chunk_count = KnowledgeChunk.objects.count()

        # Act lần 2: chạy lại cùng dữ liệu.
        second_result = rebuild_rag_index(
            embedding_model=fake_model,
            knowledge_directory=self.knowledge_directory,
        )

        # Assert: tài liệu và chunk không bị nhân đôi.
        self.assertEqual(first_result['documents'], 2)
        self.assertEqual(first_result['created_documents'], 2)
        self.assertEqual(second_result['updated_documents'], 2)

        self.assertEqual(KnowledgeBase.objects.count(), 2)
        self.assertEqual(
            KnowledgeChunk.objects.count(),
            first_chunk_count,
        )

        # Act: tìm nội dung liên quan đến thanh toán.
        results = search_knowledge(
            query='Tôi thanh toán PayOS như thế nào?',
            max_results=2,
            embedding_model=fake_model,
        )

        # Assert: tài liệu PayOS phải đứng đầu.
        self.assertGreater(len(results), 0)
        self.assertEqual(
            results[0]['title'],
            'Hướng dẫn thanh toán PayOS',
        )

        # Kiểm tra filter audience Customer.
        customer_results = search_knowledge(
            query='Tôi thanh toán PayOS như thế nào?',
            audience='CUSTOMER',
            max_results=4,
            embedding_model=fake_model,
        )

        self.assertTrue(
            all(
                result['audience'] == 'CUSTOMER'
                for result in customer_results
            )
        )

    def test_invalid_embedding_does_not_replace_old_index(self):
        # Arrange: tạo dữ liệu hợp lệ trước.
        rebuild_rag_index(
            embedding_model=FakeEmbeddingModel(),
            knowledge_directory=self.knowledge_directory,
        )

        knowledge_count = KnowledgeBase.objects.count()
        chunk_count = KnowledgeChunk.objects.count()

        # Act + Assert: vector sai số chiều phải bị từ chối.
        with self.assertRaises(ValueError):
            rebuild_rag_index(
                embedding_model=InvalidEmbeddingModel(),
                knowledge_directory=self.knowledge_directory,
            )

        # Dữ liệu cũ vẫn còn vì lỗi xảy ra trước transaction ghi mới.
        self.assertEqual(
            KnowledgeBase.objects.count(),
            knowledge_count,
        )
        self.assertEqual(
            KnowledgeChunk.objects.count(),
            chunk_count,
        )
