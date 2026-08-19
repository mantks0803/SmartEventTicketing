from decimal import Decimal

from rest_framework import serializers

from ai_agent.models import (
    ChatMessage,
    ChatSession,
    QualityLevelEnum,
    ServiceCategoryEnum,
)
from events.models import EventCategoryEnum


class ChatModeEnum:
    GENERAL = 'GENERAL'
    RECOMMEND_EVENT = 'RECOMMEND_EVENT'
    PLAN_EVENT = 'PLAN_EVENT'

    CHOICES = [
        (GENERAL, 'General'),
        (RECOMMEND_EVENT, 'Recommend event'),
        (PLAN_EVENT, 'Plan event'),
    ]


class ChatPreferencesSerializer(serializers.Serializer):
    category = serializers.ChoiceField(
        choices=EventCategoryEnum.choices,
        required=False,
    )
    location = serializers.CharField(
        max_length=250,
        required=False,
    )
    max_price = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        min_value=Decimal('0.00'),
        required=False,
    )
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    event_id = serializers.IntegerField(
        min_value=1,
        required=False,
    )
    event_name = serializers.CharField(
        max_length=250,
        required=False,
    )
    guest_count = serializers.IntegerField(
        min_value=1,
        required=False,
    )
    quality_level = serializers.ChoiceField(
        choices=QualityLevelEnum.choices,
        required=False,
    )
    service_categories = serializers.ListField(
        child=serializers.ChoiceField(
            choices=ServiceCategoryEnum.choices,
        ),
        allow_empty=False,
        required=False,
    )
    duration_hours = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        min_value=Decimal('0.01'),
        required=False,
    )

    def validate(self, attrs):
        date_from = attrs.get('date_from')
        date_to = attrs.get('date_to')

        if (
            date_from
            and date_to
            and date_from > date_to
        ):
            raise serializers.ValidationError({
                'date_to': (
                    'Ngày kết thúc không được nhỏ hơn ngày bắt đầu.'
                )
            })

        return attrs


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(
        min_length=1,
        max_length=1000,
        trim_whitespace=True,
    )
    mode = serializers.ChoiceField(
        choices=ChatModeEnum.CHOICES,
    )
    session_id = serializers.IntegerField(
        min_value=1,
        required=False,
        allow_null=True,
    )
    preferences = ChatPreferencesSerializer(
        required=False,
    )

    def validate(self, attrs):
        mode = attrs['mode']
        preferences = attrs.get('preferences') or {}

        if mode == ChatModeEnum.PLAN_EVENT:
            required_fields = [
                'category',
                'guest_count',
                'quality_level',
                'location',
                'service_categories',
            ]

            missing_fields = [
                field
                for field in required_fields
                if preferences.get(field) in (
                    None,
                    '',
                    [],
                )
            ]

            if missing_fields:
                raise serializers.ValidationError({
                    'preferences': (
                        'Chế độ tư vấn tổ chức còn thiếu: '
                        + ', '.join(missing_fields)
                        + '.'
                    )
                })

        return attrs


class ChatSessionSerializer(serializers.ModelSerializer):
    message_count = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = ChatSession
        fields = [
            'id',
            'created_at',
            'message_count',
        ]


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = [
            'id',
            'sender',
            'text',
            'timestamp',
        ]
        read_only_fields = fields
