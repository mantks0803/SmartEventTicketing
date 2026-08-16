from django.conf import settings
from django.db import models
from pgvector.django import VectorField


EMBEDDING_DIMENSIONS = 768


class KnowledgeCategoryEnum(models.TextChoices):
    GENERAL = 'GENERAL', 'General'
    POLICY = 'POLICY', 'Policy'
    PLANNING = 'PLANNING', 'Planning'
    SERVICE = 'SERVICE', 'Service'


class KnowledgeAudienceEnum(models.TextChoices):
    CUSTOMER = 'CUSTOMER', 'Customer'
    ORGANIZER = 'ORGANIZER', 'Organizer'
    ALL = 'ALL', 'All'


class ServiceCategoryEnum(models.TextChoices):
    VENUE = 'VENUE', 'Venue'
    CATERING = 'CATERING', 'Catering'
    SOUND_LIGHT = 'SOUND_LIGHT', 'Sound and light'
    DECORATION = 'DECORATION', 'Decoration'
    STAFF = 'STAFF', 'Staff'
    MEDIA = 'MEDIA', 'Media'


class QualityLevelEnum(models.TextChoices):
    ECONOMY = 'ECONOMY', 'Economy'
    STANDARD = 'STANDARD', 'Standard'
    PREMIUM = 'PREMIUM', 'Premium'


class PricingUnitEnum(models.TextChoices):
    PACKAGE = 'PACKAGE', 'Package'
    PER_PERSON = 'PER_PERSON', 'Per person'
    PER_HOUR = 'PER_HOUR', 'Per hour'


class ChatSenderEnum(models.TextChoices):
    USER = 'USER', 'User'
    ASSISTANT = 'ASSISTANT', 'Assistant'


class KnowledgeBase(models.Model):
    title = models.CharField(max_length=250)
    content = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=KnowledgeCategoryEnum.choices,
        default=KnowledgeCategoryEnum.GENERAL,
    )
    audience = models.CharField(
        max_length=20,
        choices=KnowledgeAudienceEnum.choices,
        default=KnowledgeAudienceEnum.ALL,
    )
    source_path = models.CharField(max_length=500, blank=True, default='')
    source_url = models.URLField(max_length=500, blank=True, default='')
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class KnowledgeChunk(models.Model):
    knowledge = models.ForeignKey(
        KnowledgeBase,
        on_delete=models.CASCADE,
        related_name='chunks',
    )
    chunk_index = models.PositiveIntegerField()
    content = models.TextField()
    embedding = VectorField(dimensions=EMBEDDING_DIMENSIONS)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['knowledge_id', 'chunk_index']
        constraints = [
            models.UniqueConstraint(
                fields=['knowledge', 'chunk_index'],
                name='unique_knowledge_chunk_index',
            ),
        ]

    def __str__(self):
        return f'{self.knowledge.title} - Chunk {self.chunk_index}'


class EventService(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    provider_name = models.CharField(max_length=200)
    category = models.CharField(
        max_length=30,
        choices=ServiceCategoryEnum.choices,
    )
    quality_level = models.CharField(
        max_length=20,
        choices=QualityLevelEnum.choices,
    )
    location = models.CharField(max_length=200)
    pricing_unit = models.CharField(
        max_length=20,
        choices=PricingUnitEnum.choices,
    )
    min_price = models.DecimalField(max_digits=14, decimal_places=2)
    max_price = models.DecimalField(max_digits=14, decimal_places=2)
    min_capacity = models.PositiveIntegerField()
    max_capacity = models.PositiveIntegerField()
    included_duration_hours = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )
    description = models.TextField()
    source_url = models.URLField(max_length=500, blank=True, default='')
    verified_at = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'quality_level', 'code']

    def __str__(self):
        return f'{self.name} ({self.quality_level})'


class ChatSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_sessions',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Chat #{self.id} - {self.user.username}'


class ChatMessage(models.Model):
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    sender = models.CharField(
        max_length=20,
        choices=ChatSenderEnum.choices,
    )
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender} - Chat #{self.session_id}'
