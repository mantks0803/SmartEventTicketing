import json
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase

from ai_agent.management.commands.evaluate_rag import (
    load_evaluation_cases,
)


class RagEvaluationTests(SimpleTestCase):
    def create_dataset(self, directory, cases):
        """Tạo dataset tạm để test không sửa dữ liệu thật."""

        dataset_path = Path(directory) / 'evaluation.json'
        dataset_path.write_text(
            json.dumps(
                {
                    'name': 'Test RAG Evaluation',
                    'description': 'Dataset dùng trong unit test.',
                    'cases': cases,
                },
                ensure_ascii=False,
            ),
            encoding='utf-8',
        )
        return dataset_path

    def answerable_case(self):
        return {
            'id': 'seat_hold',
            'question': 'Tôi được giữ ghế bao lâu?',
            'audience': 'CUSTOMER',
            'expected_source': 'customer/02_seat_hold.md',
            'expected_keywords': ['10 phút'],
            'should_answer': True,
            'run_generation': True,
        }

    def no_answer_case(self):
        return {
            'id': 'weather',
            'question': 'Ngày mai có mưa không?',
            'audience': 'CUSTOMER',
            'expected_source': None,
            'expected_keywords': [],
            'should_answer': False,
            'run_generation': False,
        }

    def relevant_chunk(self):
        return {
            'chunk_id': 1,
            'knowledge_id': 1,
            'title': 'Chọn ghế và giữ ghế khi mua vé',
            'content': 'Hệ thống giữ ghế trong 10 phút.',
            'category': 'POLICY',
            'audience': 'CUSTOMER',
            'source_path': 'customer/02_seat_hold.md',
            'source_url': '',
            'distance': 0.20,
        }

    def irrelevant_chunk(self):
        return {
            **self.relevant_chunk(),
            'distance': 0.85,
        }

    def test_real_dataset_has_unique_valid_cases(self):
        # Arrange: dùng chính dataset của project.
        dataset_path = (
            Path(__file__).resolve().parents[1]
            / 'data'
            / 'evaluation'
            / 'rag_questions.json'
        )

        # Act.
        dataset = load_evaluation_cases(dataset_path)

        # Assert.
        self.assertEqual(len(dataset['cases']), 30)
        self.assertEqual(
            len({case['id'] for case in dataset['cases']}),
            30,
        )
        self.assertTrue(
            any(not case['should_answer'] for case in dataset['cases'])
        )
        self.assertTrue(
            any(case['audience'] == 'ORGANIZER' for case in dataset['cases'])
        )

    @patch(
        'ai_agent.management.commands.evaluate_rag.search_knowledge'
    )
    def test_command_calculates_retrieval_metrics_and_writes_report(
        self,
        mock_search,
    ):
        # Arrange: một câu đúng source và một câu ngoài phạm vi.
        mock_search.side_effect = [
            [self.relevant_chunk()],
            [self.irrelevant_chunk()],
        ]

        with TemporaryDirectory() as temporary_directory:
            dataset_path = self.create_dataset(
                temporary_directory,
                [self.answerable_case(), self.no_answer_case()],
            )
            report_path = Path(temporary_directory) / 'report.md'
            output = StringIO()

            # Act.
            call_command(
                'evaluate_rag',
                dataset=str(dataset_path),
                top_k=4,
                report=str(report_path),
                stdout=output,
            )

            # Assert.
            command_output = output.getvalue()
            self.assertIn('Hit@4: 100.00%', command_output)
            self.assertIn('Source accuracy: 100.00%', command_output)
            self.assertIn(
                'No-answer accuracy: 100.00%',
                command_output,
            )
            self.assertTrue(report_path.exists())
            self.assertIn(
                '# Kết quả đánh giá RAG',
                report_path.read_text(encoding='utf-8'),
            )

        self.assertEqual(mock_search.call_count, 2)
        mock_search.assert_any_call(
            query='Tôi được giữ ghế bao lâu?',
            audience='CUSTOMER',
            max_results=4,
        )

    @patch(
        'ai_agent.management.commands.evaluate_rag.create_rag_chain'
    )
    @patch(
        'ai_agent.management.commands.evaluate_rag.get_chat_model'
    )
    @patch(
        'ai_agent.management.commands.evaluate_rag.search_knowledge'
    )
    def test_generation_evaluation_uses_fake_model_without_network(
        self,
        mock_search,
        mock_get_chat_model,
        mock_create_chain,
    ):
        # Arrange.
        mock_search.return_value = [self.relevant_chunk()]
        mock_get_chat_model.return_value = object()
        fake_chain = Mock()
        fake_chain.invoke.return_value = (
            'Sau khi tạo đơn, hệ thống giữ ghế trong 10 phút.'
        )
        mock_create_chain.return_value = fake_chain

        with TemporaryDirectory() as temporary_directory:
            dataset_path = self.create_dataset(
                temporary_directory,
                [self.answerable_case()],
            )
            output = StringIO()

            # Act.
            call_command(
                'evaluate_rag',
                dataset=str(dataset_path),
                with_generation=True,
                generation_limit=1,
                stdout=output,
            )

        # Assert.
        self.assertIn(
            'Generation keyword coverage: 100.00%',
            output.getvalue(),
        )
        fake_chain.invoke.assert_called_once()

    def test_dataset_rejects_duplicate_ids(self):
        # Arrange.
        duplicate_case = self.answerable_case()

        with TemporaryDirectory() as temporary_directory:
            dataset_path = self.create_dataset(
                temporary_directory,
                [duplicate_case, duplicate_case],
            )

            # Act + Assert.
            with self.assertRaisesMessage(
                ValueError,
                'ID evaluation bị trùng',
            ):
                load_evaluation_cases(dataset_path)

            with self.assertRaises(CommandError):
                call_command(
                    'evaluate_rag',
                    dataset=str(dataset_path),
                )
