from decimal import Decimal

from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.exceptions import (
    PermissionDenied,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_agent.models import (
    ChatMessage,
    ChatSenderEnum,
    ChatSession,
    KnowledgeAudienceEnum,
)
from ai_agent.rag_engine.chat_service import answer_with_rag
from ai_agent.rag_engine.event_tools import (
    check_event_availability,
    estimate_event_budget,
    recommend_events,
    suggest_ticket_price,
)
from ai_agent.serializers import (
    ChatMessageSerializer,
    ChatModeEnum,
    ChatRequestSerializer,
    ChatSessionSerializer,
)
from authentication.models import UserType
from authentication.permissions import (
    IsActiveAccountPermission,
)
from orders.services import expire_stale_orders


MEMORY_MESSAGE_LIMIT = 8


def get_user_audience(user):
    if (
        user.is_staff
        or user.is_superuser
        or user.type == UserType.ADMIN
    ):
        raise PermissionDenied(
            'Tài khoản Admin không sử dụng chatbot này.'
        )

    if user.type == UserType.CUSTOMER:
        return KnowledgeAudienceEnum.CUSTOMER

    if user.type == UserType.ORGANIZER:
        return KnowledgeAudienceEnum.ORGANIZER

    raise PermissionDenied(
        'Loại tài khoản không được phép sử dụng chatbot.'
    )


def get_user_session(user, session_id):
    if session_id is None:
        return None

    return get_object_or_404(
        ChatSession,
        id=session_id,
        user=user,
    )


def get_recent_history(session):
    if session is None:
        return []

    messages = list(
        session.messages
        .order_by('-timestamp', '-id')[
            :MEMORY_MESSAGE_LIMIT
        ]
    )

    messages.reverse()

    return [
        {
            'sender': message.sender,
            'text': message.text,
        }
        for message in messages
    ]


def build_retrieval_query(message, history):
    previous_user_message = None

    for history_message in reversed(history):
        if (
            history_message.get('sender')
            == ChatSenderEnum.USER
        ):
            previous_user_message = str(
                history_message.get('text', '')
            ).strip()
            break

    if not previous_user_message:
        return message

    return (
        f'{previous_user_message}\n'
        f'{message}'
    )


def make_json_safe(value):
    if isinstance(value, Decimal):
        return format(value, 'f')

    if isinstance(value, dict):
        return {
            key: make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            make_json_safe(item)
            for item in value
        ]

    return value


def create_empty_result():
    return {
        'answer': '',
        'sources': [],
        'recommended_events': [],
        'event_availability': None,
        'cost_breakdown': None,
        'ticket_price_suggestion': None,
    }


def process_general_mode(
    message,
    audience,
    history,
    retrieval_query,
):
    result = create_empty_result()

    rag_result = answer_with_rag(
        question=message,
        audience=audience,
        conversation_history=history,
        retrieval_query=retrieval_query,
        structured_data=None,
    )

    result['answer'] = rag_result['answer']
    result['sources'] = rag_result['sources']

    return result


def process_recommend_mode(preferences):
    result = create_empty_result()

    expire_stale_orders()

    event_id = preferences.get('event_id')
    event_name = preferences.get('event_name')

    if event_id or event_name:
        availability = check_event_availability(
            event_id=event_id,
            event_name=event_name,
        )

        result['answer'] = availability.get(
            'message',
            'Đã kiểm tra tình trạng ghế của sự kiện.',
        )
        result['event_availability'] = availability

        return result

    events = recommend_events(
        category=preferences.get('category'),
        location=preferences.get('location'),
        max_price=preferences.get('max_price'),
        date_from=preferences.get('date_from'),
        date_to=preferences.get('date_to'),
    )

    result['recommended_events'] = events

    if events:
        result['answer'] = (
            f'Tôi tìm thấy {len(events)} sự kiện phù hợp. '
            'Bạn có thể xem thông tin chi tiết bên dưới.'
        )
    else:
        result['answer'] = (
            'Hiện chưa tìm thấy sự kiện phù hợp với '
            'các điều kiện bạn đã chọn.'
        )

    return result


def process_plan_mode(
    message,
    audience,
    history,
    retrieval_query,
    preferences,
):
    result = create_empty_result()

    budget = estimate_event_budget(
        guest_count=preferences['guest_count'],
        quality_level=preferences['quality_level'],
        location=preferences['location'],
        service_categories=(
            preferences['service_categories']
        ),
        duration_hours=preferences.get(
            'duration_hours'
        ),
    )

    ticket_price = suggest_ticket_price(
        total_estimated_cost=(
            budget['total_estimated_cost']
        ),
        guest_count=preferences['guest_count'],
        category=preferences['category'],
    )

    structured_data = {
        'budget': budget,
        'ticket_price': ticket_price,
    }

    rag_result = answer_with_rag(
        question=message,
        audience=audience,
        conversation_history=history,
        retrieval_query=retrieval_query,
        structured_data=structured_data,
    )

    result['answer'] = rag_result['answer']
    result['sources'] = rag_result['sources']
    result['cost_breakdown'] = budget
    result['ticket_price_suggestion'] = ticket_price

    return result


def dispatch_chat(
    mode,
    message,
    audience,
    history,
    retrieval_query,
    preferences,
):
    if mode == ChatModeEnum.GENERAL:
        return process_general_mode(
            message=message,
            audience=audience,
            history=history,
            retrieval_query=retrieval_query,
        )

    if mode == ChatModeEnum.RECOMMEND_EVENT:
        return process_recommend_mode(
            preferences=preferences,
        )

    return process_plan_mode(
        message=message,
        audience=audience,
        history=history,
        retrieval_query=retrieval_query,
        preferences=preferences,
    )


class ChatView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        IsActiveAccountPermission,
    ]

    def post(self, request):
        serializer = ChatRequestSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        message = validated_data['message']
        mode = validated_data['mode']
        session_id = validated_data.get('session_id')
        preferences = (
            validated_data.get('preferences')
            or {}
        )

        audience = get_user_audience(request.user)

        session = get_user_session(
            request.user,
            session_id,
        )

        history = get_recent_history(session)

        retrieval_query = build_retrieval_query(
            message,
            history,
        )

        try:
            result = dispatch_chat(
                mode=mode,
                message=message,
                audience=audience,
                history=history,
                retrieval_query=retrieval_query,
                preferences=preferences,
            )
        except ValueError as error:
            raise ValidationError({
                'preferences': [str(error)]
            }) from error

        with transaction.atomic():
            if session is None:
                session = ChatSession.objects.create(
                    user=request.user,
                )

            ChatMessage.objects.create(
                session=session,
                sender=ChatSenderEnum.USER,
                text=message,
            )

            ChatMessage.objects.create(
                session=session,
                sender=ChatSenderEnum.ASSISTANT,
                text=result['answer'],
            )

        response_data = {
            'session_id': session.id,
            'mode': mode,
            **result,
        }

        return Response(
            make_json_safe(response_data),
            status=status.HTTP_200_OK,
        )


class ChatSessionListView(generics.ListAPIView):
    serializer_class = ChatSessionSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsActiveAccountPermission,
    ]

    def get_queryset(self):
        get_user_audience(self.request.user)

        return (
            ChatSession.objects
            .filter(user=self.request.user)
            .annotate(
                message_count=Count('messages')
            )
            .order_by('-created_at', '-id')
        )


class ChatSessionMessageListView(
    generics.ListAPIView
):
    serializer_class = ChatMessageSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsActiveAccountPermission,
    ]

    def get_queryset(self):
        get_user_audience(self.request.user)

        session = get_object_or_404(
            ChatSession,
            id=self.kwargs['session_id'],
            user=self.request.user,
        )

        return (
            session.messages
            .order_by('timestamp', 'id')
        )
