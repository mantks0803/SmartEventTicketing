from unittest.mock import patch

from django.test import SimpleTestCase, override_settings
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from ai_agent.rag_engine.chat_service import (
    AI_UNAVAILABLE_MESSAGE,
    NO_INFORMATION_MESSAGE,
    answer_with_rag,
    build_context,
    build_sources,
    get_chat_model,
)


class FakeChatModel:
    """Chat model giả, không gọi Gemini thật trong test."""

    def __init__(self, answer='Câu trả lời giả.', should_raise=False):
        self.answer = answer
        self.should_raise = should_raise
        self.call_count = 0
        self.last_input = None
        self.runnable = RunnableLambda(self.invoke)

    def invoke(self, input_value):
        self.call_count += 1
        self.last_input = input_value

        if self.should_raise:
            raise RuntimeError('Gemini test error')

        return AIMessage(content=self.answer)


class ChatServiceTests(SimpleTestCase):
    def setUp(self):
        self.payment_chunks = [
            {
                'chunk_id': 1,
                'knowledge_id': 1,
                'title': 'Thanh toán đơn hàng qua PayOS',
                'content': (
                    'Khách hàng thanh toán đơn hàng qua PayOS. '
                    'Sau khi thanh toán thành công, hệ thống '
                    'phát hành vé điện tử.'
                ),
                'category': 'POLICY',
                'audience': 'CUSTOMER',
                'source_path': 'customer/03_payos_payment.md',
                'source_url': '',
                'distance': 0.20,
            },
            {
                'chunk_id': 2,
                'knowledge_id': 1,
                'title': 'Thanh toán đơn hàng qua PayOS',
                'content': (
                    'Vé đã thanh toán được hiển thị tại trang Vé của tôi.'
                ),
                'category': 'POLICY',
                'audience': 'CUSTOMER',
                'source_path': 'customer/03_payos_payment.md',
                'source_url': '',
                'distance': 0.25,
            },
        ]

    def test_build_context_and_sources_remove_duplicate_source(self):
        # Act.
        context = build_context(self.payment_chunks)
        sources = build_sources(self.payment_chunks)

        # Assert.
        self.assertIn('[1]', context)
        self.assertIn('[2]', context)
        self.assertIn('Thanh toán đơn hàng qua PayOS', context)
        self.assertIn('Vé của tôi', context)

        # Hai chunk cùng tài liệu chỉ tạo một source.
        self.assertEqual(len(sources), 1)
        self.assertEqual(
            sources[0]['source_path'],
            'customer/03_payos_payment.md',
        )

    @patch('ai_agent.rag_engine.chat_service.search_knowledge')
    def test_answer_with_rag_returns_answer_and_sources(
        self,
        mock_search_knowledge,
    ):
        # Arrange.
        mock_search_knowledge.return_value = self.payment_chunks
        fake_chat = FakeChatModel(
            answer=(
                'Sau khi thanh toán thành công, '
                'bạn có thể xem vé tại trang Vé của tôi.'
            )
        )
        fake_embedding = object()

        # Act.
        result = answer_with_rag(
            question='Thanh toán xong tôi xem vé ở đâu?',
            audience='CUSTOMER',
            max_results=4,
            embedding_model=fake_embedding,
            chat_model=fake_chat.runnable,
        )

        # Assert.
        self.assertEqual(fake_chat.call_count, 1)
        self.assertIn('Vé của tôi', result['answer'])
        self.assertEqual(len(result['sources']), 1)
        self.assertEqual(
            result['sources'][0]['source_path'],
            'customer/03_payos_payment.md',
        )

        mock_search_knowledge.assert_called_once_with(
            query='Thanh toán xong tôi xem vé ở đâu?',
            audience='CUSTOMER',
            max_results=4,
            embedding_model=fake_embedding,
        )

        # Prompt phải có cả câu hỏi và context tìm được.
        messages = fake_chat.last_input.to_messages()
        prompt_content = '\n'.join(
            str(message.content)
            for message in messages
        )

        self.assertIn(
            'Thanh toán xong tôi xem vé ở đâu?',
            prompt_content,
        )
        self.assertIn('phát hành vé điện tử', prompt_content)

    @patch('ai_agent.rag_engine.chat_service.search_knowledge')
    def test_empty_search_does_not_call_chat_model(
        self,
        mock_search_knowledge,
    ):
        mock_search_knowledge.return_value = []
        fake_chat = FakeChatModel()

        result = answer_with_rag(
            question='Một câu hỏi không có tài liệu',
            audience='CUSTOMER',
            chat_model=fake_chat.runnable,
        )

        self.assertEqual(result['answer'], NO_INFORMATION_MESSAGE)
        self.assertEqual(result['sources'], [])
        self.assertEqual(fake_chat.call_count, 0)

    @patch('ai_agent.rag_engine.chat_service.search_knowledge')
    def test_irrelevant_chunks_do_not_call_chat_model(
        self,
        mock_search_knowledge,
    ):
        irrelevant_chunk = {
            **self.payment_chunks[0],
            'distance': 0.90,
        }
        mock_search_knowledge.return_value = [irrelevant_chunk]
        fake_chat = FakeChatModel()

        result = answer_with_rag(
            question='Thời tiết hôm nay thế nào?',
            audience='CUSTOMER',
            chat_model=fake_chat.runnable,
        )

        self.assertEqual(result['answer'], NO_INFORMATION_MESSAGE)
        self.assertEqual(result['sources'], [])
        self.assertEqual(fake_chat.call_count, 0)

    @patch('ai_agent.rag_engine.chat_service.logger.exception')
    @patch('ai_agent.rag_engine.chat_service.search_knowledge')
    def test_chat_model_error_returns_safe_fallback(
        self,
        mock_search_knowledge,
        mock_logger,
    ):
        mock_search_knowledge.return_value = self.payment_chunks
        fake_chat = FakeChatModel(should_raise=True)

        result = answer_with_rag(
            question='Thanh toán PayOS như thế nào?',
            audience='CUSTOMER',
            chat_model=fake_chat.runnable,
        )

        self.assertEqual(fake_chat.call_count, 1)
        self.assertEqual(result['answer'], AI_UNAVAILABLE_MESSAGE)

        # Retrieval thành công nên nguồn vẫn được giữ lại.
        self.assertEqual(len(result['sources']), 1)
        mock_logger.assert_called_once()

    @patch('ai_agent.rag_engine.chat_service.logger.exception')
    @patch('ai_agent.rag_engine.chat_service.search_knowledge')
    def test_retrieval_error_returns_safe_fallback(
        self,
        mock_search_knowledge,
        mock_logger,
    ):
        mock_search_knowledge.side_effect = RuntimeError(
            'Embedding API error'
        )
        fake_chat = FakeChatModel()

        result = answer_with_rag(
            question='Tôi được giữ ghế trong bao lâu?',
            audience='CUSTOMER',
            chat_model=fake_chat.runnable,
        )

        self.assertEqual(result['answer'], AI_UNAVAILABLE_MESSAGE)
        self.assertEqual(result['sources'], [])
        self.assertEqual(fake_chat.call_count, 0)
        mock_logger.assert_called_once()

    @override_settings(GOOGLE_API_KEY='')
    def test_get_chat_model_requires_api_key(self):
        with self.assertRaisesMessage(
            ValueError,
            'Chưa cấu hình GOOGLE_API_KEY',
        ):
            get_chat_model()
