from django.contrib import admin

from ai_agent.models import (
    ChatMessage,
    ChatSession,
    EventService,
    KnowledgeBase,
    KnowledgeChunk,
)


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'audience', 'is_active', 'updated_at')
    list_filter = ('category', 'audience', 'is_active')
    search_fields = ('title', 'content', 'source_path')


@admin.register(KnowledgeChunk)
class KnowledgeChunkAdmin(admin.ModelAdmin):
    list_display = ('knowledge', 'chunk_index', 'created_at')
    search_fields = ('knowledge__title', 'content')
    list_select_related = ('knowledge',)


@admin.register(EventService)
class EventServiceAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'name', 'category', 'quality_level',
        'min_price', 'max_price', 'is_active',
    )
    list_filter = ('category', 'quality_level', 'pricing_unit', 'is_active')
    search_fields = ('code', 'name', 'provider_name', 'location')


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')
    search_fields = ('user__username', 'user__email')
    list_select_related = ('user',)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'sender', 'timestamp')
    list_filter = ('sender',)
    search_fields = ('text', 'session__user__username')
    list_select_related = ('session', 'session__user')
