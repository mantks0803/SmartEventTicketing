import math
import re
import time
from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pgvector.django import CosineDistance

from ai_agent.models import (
    EMBEDDING_DIMENSIONS,
    KnowledgeAudienceEnum,
    KnowledgeBase,
    KnowledgeCategoryEnum,
    KnowledgeChunk,
)


KNOWLEDGE_DIRECTORY = (
    Path(settings.BASE_DIR)
    / 'ai_agent'
    / 'data'
    / 'knowledge'
)

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 120
EMBEDDING_REQUEST_INTERVAL = 2
EMBEDDING_MAX_RETRIES = 3

CATEGORY_PATTERN = re.compile(
    r'^>\s*Danh mục kiến thức:\s*([A-Z_]+)',
    re.MULTILINE | re.IGNORECASE,
)


def get_embedding_model():

    if not settings.GOOGLE_API_KEY:
        raise ValueError(
            'Chưa cấu hình GOOGLE_API_KEY trong file backend/.env.'
        )

    validate_embedding_configuration()

    return GoogleGenerativeAIEmbeddings(
        model=settings.AI_EMBEDDING_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        output_dimensionality=settings.AI_EMBEDDING_DIMENSIONS,
    )


def validate_embedding_configuration():

    configured_dimensions = settings.AI_EMBEDDING_DIMENSIONS

    if configured_dimensions != EMBEDDING_DIMENSIONS:
        raise ValueError(
            'AI_EMBEDDING_DIMENSIONS phải bằng '
            f'{EMBEDDING_DIMENSIONS} để khớp với KnowledgeChunk.embedding.'
        )


def get_document_title(content, file_path):

    for line in content.splitlines():
        line = line.strip()

        if line.startswith('# '):
            return line[2:].strip()

    # Dùng tên file nếu tài liệu không có tiêu đề Markdown.
    return file_path.stem.replace('_', ' ').strip()


def get_document_category(content, file_path):
    """Đọc danh mục kiến thức từ phần thông tin đầu tài liệu."""

    match = CATEGORY_PATTERN.search(content)

    if not match:
        return KnowledgeCategoryEnum.GENERAL

    category = match.group(1).strip().upper()

    if category not in KnowledgeCategoryEnum.values:
        raise ValueError(
            f'Danh mục kiến thức không hợp lệ trong file {file_path.name}: '
            f'{category}.'
        )

    return category


def load_markdown_documents(knowledge_directory=None):

    root_directory = Path(
        knowledge_directory or KNOWLEDGE_DIRECTORY
    )

    if not root_directory.exists():
        raise ValueError(
            f'Không tìm thấy thư mục tài liệu: {root_directory}'
        )

    audience_folders = {
        KnowledgeAudienceEnum.CUSTOMER: 'customer',
        KnowledgeAudienceEnum.ORGANIZER: 'organizer',
    }

    documents = []

    for audience, folder_name in audience_folders.items():
        audience_directory = root_directory / folder_name

        if not audience_directory.exists():
            continue

        for file_path in sorted(audience_directory.rglob('*.md')):
            content = file_path.read_text(encoding='utf-8').strip()

            if not content:
                continue

            documents.append({
                'title': get_document_title(content, file_path),
                'content': content,
                'category': get_document_category(content, file_path),
                'audience': audience,
                'source_path': file_path.relative_to(
                    root_directory
                ).as_posix(),
                'source_url': '',
            })

    if not documents:
        raise ValueError(
            f'Không tìm thấy tài liệu Markdown trong {root_directory}.'
        )

    return documents


def split_document(content):

    if not content or not content.strip():
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[
            '\n## ',
            '\n### ',
            '\n\n',
            '\n',
            '. ',
            ' ',
            '',
        ],
    )

    chunks = splitter.split_text(content)

    return [
        chunk.strip()
        for chunk in chunks
        if chunk.strip()
    ]


def validate_embedding_vector(vector):
    if len(vector) != EMBEDDING_DIMENSIONS:
        raise ValueError(
            'Embedding trả về sai số chiều. '
            f'Cần {EMBEDDING_DIMENSIONS}, nhận được {len(vector)}.'
        )


def get_embedding_retry_delay(error):
    api_error = error.__cause__ or error
    message = f'{error} {api_error}'

    if (
        getattr(api_error, 'code', None) != 429
        and 'RESOURCE_EXHAUSTED' not in message.upper()
    ):
        return None

    if re.search(r'per\s*day|daily|limit:\s*0\b', message, re.IGNORECASE):
        return None

    retry_match = re.search(
        r'retry in\s+(\d+(?:\.\d+)?)s',
        message,
        re.IGNORECASE,
    )
    if not retry_match:
        retry_match = re.search(
            r"retryDelay[\"'\s:]+(\d+(?:\.\d+)?)s",
            message,
            re.IGNORECASE,
        )

    if retry_match:
        return max(2, math.ceil(float(retry_match.group(1))) + 2)

    return 60


def embed_documents_with_retry(model, texts, progress_callback=None):
    embeddings = []

    for index, text in enumerate(texts, start=1):
        time.sleep(EMBEDDING_REQUEST_INTERVAL)

        for attempt in range(EMBEDDING_MAX_RETRIES + 1):
            try:
                result = model.embed_documents([text])
            except Exception as exc:
                wait_seconds = get_embedding_retry_delay(exc)
                if wait_seconds is None:
                    raise

                if attempt == EMBEDDING_MAX_RETRIES:
                    raise RuntimeError(
                        'Google vẫn giới hạn embedding sau 3 lần thử lại. '
                        'Hãy kiểm tra hạn mức trong Google AI Studio. '
                        'Bộ kiến thức cũ trong database chưa bị thay đổi.'
                    ) from exc

                if progress_callback:
                    progress_callback(
                        f'Google báo 429 tại đoạn {index}/{len(texts)}. '
                        f'Chờ {wait_seconds} giây rồi thử lại '
                        f'({attempt + 1}/{EMBEDDING_MAX_RETRIES})...'
                    )

                while wait_seconds > 0:
                    pause = min(30, wait_seconds)
                    time.sleep(pause)
                    wait_seconds -= pause
                continue

            if len(result) != 1:
                raise ValueError('Google phải trả đúng một vector cho mỗi đoạn.')

            validate_embedding_vector(result[0])
            embeddings.append(result[0])

            if progress_callback:
                progress_callback(f'  Đã tạo embedding đoạn {index}/{len(texts)}.')
            break

    return embeddings


def rebuild_rag_index(
    embedding_model=None,
    knowledge_directory=None,
    progress_callback=None,
):
 

    validate_embedding_configuration()

    documents = load_markdown_documents(knowledge_directory)
    model = embedding_model or get_embedding_model()

    prepared_documents = []
    total_chunks = 0

    for document in documents:
        chunks = split_document(document['content'])

        if not chunks:
            raise ValueError(
                f'Tài liệu {document["source_path"]} không tạo được chunk.'
            )

        if progress_callback:
            progress_callback(
                f'Đang xử lý {document["source_path"]} '
                f'({len(chunks)} đoạn)...'
            )

        embedding_texts = [ 
            f'{document["title"]}\n\n{chunk}'
            for chunk in chunks
        ]

        embeddings = embed_documents_with_retry(
            model,
            embedding_texts,
            progress_callback=progress_callback,
        )

        if len(embeddings) != len(chunks):
            raise ValueError(
                f'Số embedding không khớp số chunk của '
                f'{document["source_path"]}.'
            )

        for vector in embeddings:
            validate_embedding_vector(vector)

        prepared_documents.append({
            'document': document,
            'chunks': chunks,
            'embeddings': embeddings,
        })

        total_chunks += len(chunks)

    created_documents = 0
    updated_documents = 0
    source_paths = [
        item['document']['source_path']
        for item in prepared_documents
    ]

    with transaction.atomic():
        for item in prepared_documents:
            document = item['document']

            knowledge, created = KnowledgeBase.objects.update_or_create(
                source_path=document['source_path'],
                defaults={
                    'title': document['title'],
                    'content': document['content'],
                    'category': document['category'],
                    'audience': document['audience'],
                    'source_url': document['source_url'],
                    'is_active': True,
                },
            )

            if created:
                created_documents += 1
            else:
                updated_documents += 1

            knowledge.chunks.all().delete()

            new_chunks = []

            for index, chunk in enumerate(item['chunks']):
                new_chunks.append(
                    KnowledgeChunk(
                        knowledge=knowledge,
                        chunk_index=index,
                        content=chunk,
                        embedding=item['embeddings'][index],
                    )
                )

            KnowledgeChunk.objects.bulk_create(new_chunks)

        stale_documents = KnowledgeBase.objects.filter(
            Q(source_path__startswith='customer/')
            | Q(source_path__startswith='organizer/')
        ).exclude(source_path__in=source_paths)

        deleted_documents = stale_documents.count()
        stale_documents.delete()

    return {
        'documents': len(prepared_documents),
        'chunks': total_chunks,
        'created_documents': created_documents,
        'updated_documents': updated_documents,
        'deleted_documents': deleted_documents,
    }


def search_knowledge(
    query,
    audience=None,
    max_results=None,
    embedding_model=None,
):
    """Tìm các chunk gần với câu hỏi bằng cosine distance."""

    query = str(query).strip()

    if not query:
        raise ValueError('Câu hỏi tìm kiếm không được để trống.')

    validate_embedding_configuration()

    selected_audience = None

    if audience:
        selected_audience = str(audience).strip().upper()

        if selected_audience not in KnowledgeAudienceEnum.values:
            raise ValueError(
                f'Đối tượng tài liệu không hợp lệ: {selected_audience}.'
            )

    result_limit = (
        max_results
        if max_results is not None
        else settings.AI_MAX_CONTEXT_CHUNKS
    )

    try:
        result_limit = int(result_limit)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            'Số lượng kết quả tìm kiếm phải là số nguyên.'
        ) from exc

    if result_limit <= 0:
        raise ValueError(
            'Số lượng kết quả tìm kiếm phải lớn hơn 0.'
        )

    model = embedding_model or get_embedding_model()
    query_embedding = model.embed_query(query)

    validate_embedding_vector(query_embedding)

    chunks = KnowledgeChunk.objects.select_related(
        'knowledge'
    ).filter(
        knowledge__is_active=True
    )

    #Quy dinh ai duoc xem tai lieu gi
    if (
        selected_audience
        and selected_audience != KnowledgeAudienceEnum.ALL
    ):
        chunks = chunks.filter(
            Q(knowledge__audience=selected_audience)
            | Q(knowledge__audience=KnowledgeAudienceEnum.ALL)
        )

    chunks = chunks.annotate(
        distance=CosineDistance(
            'embedding',
            query_embedding,
        )
    ).order_by(
        'distance',
        'id',
    )[:result_limit]

    return [
        {
            'chunk_id': chunk.id,
            'knowledge_id': chunk.knowledge_id,
            'title': chunk.knowledge.title,
            'content': chunk.content,
            'category': chunk.knowledge.category,
            'audience': chunk.knowledge.audience,
            'source_path': chunk.knowledge.source_path,
            'source_url': chunk.knowledge.source_url,
            'distance': float(chunk.distance),
        }
        for chunk in chunks
    ]
