import json
import sys
from datetime import datetime
from pathlib import Path
from time import perf_counter

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from ai_agent.rag_engine.chat_service import (
    build_context,
    create_rag_chain,
    filter_relevant_chunks,
    get_chat_model,
)
from ai_agent.rag_engine.rag_indexer import search_knowledge


DEFAULT_DATASET = (
    Path(settings.BASE_DIR)
    / 'ai_agent'
    / 'data'
    / 'evaluation'
    / 'rag_questions.json'
)

ALLOWED_AUDIENCES = {'CUSTOMER', 'ORGANIZER'}


def load_evaluation_cases(dataset_path):
    """Đọc và kiểm tra bộ câu hỏi evaluation."""

    dataset_path = Path(dataset_path)

    if not dataset_path.exists():
        raise ValueError(
            f'Không tìm thấy file evaluation: {dataset_path}'
        )

    try:
        data = json.loads(dataset_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f'File evaluation không phải JSON hợp lệ: {exc}'
        ) from exc

    if not isinstance(data, dict):
        raise ValueError('File evaluation phải là một JSON object.')

    cases = data.get('cases')

    if not isinstance(cases, list) or not cases:
        raise ValueError(
            'File evaluation phải có danh sách cases không rỗng.'
        )

    validated_cases = []
    used_ids = set()

    for index, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            raise ValueError(f'Case thứ {index} phải là JSON object.')

        case_id = str(case.get('id', '')).strip()
        question = str(case.get('question', '')).strip()
        audience = str(case.get('audience', '')).strip().upper()
        expected_source = case.get('expected_source')
        expected_keywords = case.get('expected_keywords', [])
        should_answer = case.get('should_answer')
        run_generation = case.get('run_generation', False)

        if not case_id:
            raise ValueError(f'Case thứ {index} chưa có id.')

        if case_id in used_ids:
            raise ValueError(f'ID evaluation bị trùng: {case_id}.')

        if not question:
            raise ValueError(f'Case {case_id} chưa có question.')

        if audience not in ALLOWED_AUDIENCES:
            raise ValueError(
                f'Case {case_id} có audience không hợp lệ: {audience}.'
            )

        if not isinstance(should_answer, bool):
            raise ValueError(
                f'Case {case_id} phải có should_answer là boolean.'
            )

        if not isinstance(run_generation, bool):
            raise ValueError(
                f'Case {case_id} phải có run_generation là boolean.'
            )

        if not isinstance(expected_keywords, list):
            raise ValueError(
                f'Case {case_id} phải có expected_keywords là danh sách.'
            )

        expected_keywords = [
            str(keyword).strip()
            for keyword in expected_keywords
            if str(keyword).strip()
        ]

        if should_answer:
            expected_source = str(expected_source or '').strip()

            if not expected_source:
                raise ValueError(
                    f'Case {case_id} cần expected_source.'
                )
        else:
            expected_source = None

        used_ids.add(case_id)
        validated_cases.append({
            'id': case_id,
            'question': question,
            'audience': audience,
            'expected_source': expected_source,
            'expected_keywords': expected_keywords,
            'should_answer': should_answer,
            'run_generation': run_generation,
        })

    return {
        'name': str(data.get('name', 'RAG Evaluation')).strip(),
        'description': str(data.get('description', '')).strip(),
        'cases': validated_cases,
    }


def get_source_paths(chunks):
    """Lấy source_path duy nhất theo đúng thứ tự retrieval."""

    source_paths = []

    for chunk in chunks:
        source_path = str(chunk.get('source_path', '')).strip()

        if source_path and source_path not in source_paths:
            source_paths.append(source_path)

    return source_paths


def percentage(part, total):
    """Tính phần trăm và tránh lỗi chia cho 0."""

    if total == 0:
        return 0.0

    return round(part * 100 / total, 2)


def markdown_cell(value):
    """Làm sạch dữ liệu trước khi đưa vào bảng Markdown."""

    return str(value).replace('|', '\\|').replace('\n', ' ').strip()


def build_markdown_report(dataset, summary, results):
    """Tạo nội dung báo cáo Markdown từ kết quả evaluation."""

    generated_at = datetime.now().astimezone().strftime(
        '%d/%m/%Y %H:%M:%S %Z'
    )

    lines = [
        '# Kết quả đánh giá RAG',
        '',
        f'- Bộ dữ liệu: **{dataset["name"]}**',
        f'- Thời gian chạy: **{generated_at}**',
        f'- Tổng số câu hỏi: **{summary["total_cases"]}**',
        f'- Top K: **{summary["top_k"]}**',
        '',
        '## Chỉ số tổng hợp',
        '',
        '| Chỉ số | Kết quả |',
        '|---|---:|',
        (
            f'| Hit@{summary["top_k"]} | '
            f'{summary["hit_rate"]:.2f}% |'
        ),
        (
            '| Source accuracy sau relevance filter | '
            f'{summary["source_accuracy"]:.2f}% |'
        ),
        (
            '| No-answer accuracy | '
            f'{summary["no_answer_accuracy"]:.2f}% |'
        ),
        (
            '| Answer decision accuracy | '
            f'{summary["answer_decision_accuracy"]:.2f}% |'
        ),
        (
            '| Retrieval latency trung bình | '
            f'{summary["average_latency_ms"]:.2f} ms |'
        ),
    ]

    if summary['generation_cases']:
        lines.extend([
            (
                '| Generation keyword coverage | '
                f'{summary["generation_keyword_coverage"]:.2f}% |'
            ),
            (
                '| Số câu generation đã chạy | '
                f'{summary["generation_cases"]} |'
            ),
        ])

    lines.extend([
        '',
        '## Chi tiết từng câu hỏi',
        '',
        '| ID | Vai trò | Nguồn mong đợi | Nguồn đầu tiên | '
        'Distance | Kết quả |',
        '|---|---|---|---|---:|---|',
    ])

    for result in results:
        first_source = (
            result['retrieved_sources'][0]
            if result['retrieved_sources']
            else '-'
        )
        distance = (
            f'{result["minimum_distance"]:.4f}'
            if result['minimum_distance'] is not None
            else '-'
        )

        lines.append(
            f'| {markdown_cell(result["id"])} '
            f'| {markdown_cell(result["audience"])} '
            f'| {markdown_cell(result["expected_source"] or "-")} '
            f'| {markdown_cell(first_source)} '
            f'| {distance} '
            f'| {"PASS" if result["passed"] else "FAIL"} |'
        )

    lines.extend([
        '',
        '## Cách hiểu kết quả',
        '',
        '- `Hit@K`: nguồn đúng xuất hiện trong K kết quả retrieval đầu tiên.',
        '- `Source accuracy`: nguồn đúng vẫn còn sau khi lọc relevance.',
        '- `No-answer accuracy`: câu ngoài phạm vi được từ chối đúng.',
        '- `Generation keyword coverage`: câu trả lời chứa các ý bắt buộc.',
        '',
        '> Kết quả phụ thuộc model embedding, tài liệu và cấu hình hiện tại.',
    ])

    return '\n'.join(lines) + '\n'


class Command(BaseCommand):
    help = 'Đánh giá chất lượng retrieval và generation của RAG.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dataset',
            default=str(DEFAULT_DATASET),
            help='Đường dẫn file JSON chứa bộ câu hỏi evaluation.',
        )
        parser.add_argument(
            '--top-k',
            type=int,
            default=4,
            help='Số chunk retrieval được lấy cho mỗi câu hỏi.',
        )
        parser.add_argument(
            '--with-generation',
            action='store_true',
            help='Gọi Gemini Chat cho các case được đánh dấu.',
        )
        parser.add_argument(
            '--generation-limit',
            type=int,
            default=5,
            help='Số câu generation tối đa để bảo vệ quota.',
        )
        parser.add_argument(
            '--report',
            default='',
            help='Đường dẫn tùy chọn để lưu báo cáo Markdown.',
        )

    def handle(self, *args, **options):
        # Command Prompt Windows cần UTF-8 để in tiếng Việt.
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')

        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')

        top_k = options['top_k']
        generation_limit = options['generation_limit']

        if top_k <= 0:
            raise CommandError('--top-k phải lớn hơn 0.')

        if generation_limit <= 0:
            raise CommandError('--generation-limit phải lớn hơn 0.')

        try:
            dataset = load_evaluation_cases(options['dataset'])
        except ValueError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f'Đang đánh giá: {dataset["name"]}'
            )
        )

        results = []
        generation_chain = None
        generation_count = 0

        for index, case in enumerate(dataset['cases'], start=1):
            started_at = perf_counter()

            try:
                chunks = search_knowledge(
                    query=case['question'],
                    audience=case['audience'],
                    max_results=top_k,
                )
            except Exception as exc:
                raise CommandError(
                    f'Không thể retrieval case {case["id"]}: {exc}'
                ) from exc

            latency_ms = (perf_counter() - started_at) * 1000
            relevant_chunks = filter_relevant_chunks(chunks)
            retrieved_sources = get_source_paths(chunks)
            relevant_sources = get_source_paths(relevant_chunks)
            minimum_distance = (
                min(float(chunk['distance']) for chunk in chunks)
                if chunks
                else None
            )

            if case['should_answer']:
                retrieval_hit = (
                    case['expected_source'] in retrieved_sources
                )
                source_correct = (
                    case['expected_source'] in relevant_sources
                )
                answer_decision_correct = bool(relevant_chunks)
                passed = source_correct and answer_decision_correct
            else:
                retrieval_hit = None
                source_correct = None
                answer_decision_correct = not relevant_chunks
                passed = answer_decision_correct

            result = {
                'id': case['id'],
                'audience': case['audience'],
                'expected_source': case['expected_source'],
                'retrieved_sources': retrieved_sources,
                'relevant_sources': relevant_sources,
                'minimum_distance': minimum_distance,
                'latency_ms': latency_ms,
                'retrieval_hit': retrieval_hit,
                'source_correct': source_correct,
                'answer_decision_correct': answer_decision_correct,
                'generation_checked': False,
                'generation_keyword_passed': None,
                'passed': passed,
            }

            should_run_generation = (
                options['with_generation']
                and case['run_generation']
                and generation_count < generation_limit
            )

            if should_run_generation:
                generation_count += 1
                result['generation_checked'] = True

                if relevant_chunks:
                    try:
                        if generation_chain is None:
                            generation_chain = create_rag_chain(
                                get_chat_model()
                            )

                        answer = generation_chain.invoke({
                            'context': build_context(relevant_chunks),
                            'question': case['question'],
                        })
                        answer_text = str(answer).strip().casefold()
                        result['generation_keyword_passed'] = all(
                            keyword.casefold() in answer_text
                            for keyword in case['expected_keywords']
                        )
                    except Exception as exc:
                        raise CommandError(
                            'Không thể chạy generation case '
                            f'{case["id"]}: {exc}'
                        ) from exc
                else:
                    result['generation_keyword_passed'] = False

                result['passed'] = (
                    result['passed']
                    and result['generation_keyword_passed']
                )

            results.append(result)
            status_text = 'PASS' if result['passed'] else 'FAIL'
            status_style = (
                self.style.SUCCESS
                if result['passed']
                else self.style.ERROR
            )
            distance_text = (
                f'{minimum_distance:.4f}'
                if minimum_distance is not None
                else '-'
            )

            self.stdout.write(
                f'[{index:02d}/{len(dataset["cases"]):02d}] '
                f'{status_style(status_text)} '
                f'{case["id"]} - distance={distance_text}'
            )

        answerable_results = [
            result
            for result, case in zip(results, dataset['cases'])
            if case['should_answer']
        ]
        no_answer_results = [
            result
            for result, case in zip(results, dataset['cases'])
            if not case['should_answer']
        ]
        generation_results = [
            result
            for result in results
            if result['generation_checked']
        ]

        summary = {
            'total_cases': len(results),
            'top_k': top_k,
            'hit_rate': percentage(
                sum(
                    result['retrieval_hit'] is True
                    for result in answerable_results
                ),
                len(answerable_results),
            ),
            'source_accuracy': percentage(
                sum(
                    result['source_correct'] is True
                    for result in answerable_results
                ),
                len(answerable_results),
            ),
            'no_answer_accuracy': percentage(
                sum(
                    result['answer_decision_correct']
                    for result in no_answer_results
                ),
                len(no_answer_results),
            ),
            'answer_decision_accuracy': percentage(
                sum(
                    result['answer_decision_correct']
                    for result in results
                ),
                len(results),
            ),
            'average_latency_ms': round(
                sum(result['latency_ms'] for result in results)
                / len(results),
                2,
            ),
            'generation_cases': len(generation_results),
            'generation_keyword_coverage': percentage(
                sum(
                    result['generation_keyword_passed'] is True
                    for result in generation_results
                ),
                len(generation_results),
            ),
        }

        self.stdout.write('')
        self.stdout.write(self.style.MIGRATE_HEADING('Tổng kết'))
        self.stdout.write(
            f'- Hit@{top_k}: {summary["hit_rate"]:.2f}%'
        )
        self.stdout.write(
            '- Source accuracy: '
            f'{summary["source_accuracy"]:.2f}%'
        )
        self.stdout.write(
            '- No-answer accuracy: '
            f'{summary["no_answer_accuracy"]:.2f}%'
        )
        self.stdout.write(
            '- Answer decision accuracy: '
            f'{summary["answer_decision_accuracy"]:.2f}%'
        )
        self.stdout.write(
            '- Retrieval latency trung bình: '
            f'{summary["average_latency_ms"]:.2f} ms'
        )

        if generation_results:
            self.stdout.write(
                '- Generation keyword coverage: '
                f'{summary["generation_keyword_coverage"]:.2f}% '
                f'({len(generation_results)} câu)'
            )

        if options['report']:
            report_path = Path(options['report'])

            if not report_path.is_absolute():
                report_path = Path.cwd() / report_path

            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(
                build_markdown_report(dataset, summary, results),
                encoding='utf-8',
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Đã lưu báo cáo: {report_path.resolve()}'
                )
            )
