from django.contrib import admin
from ai_agent.models import KnowledgeBase, ChatSession, ChatMessage

admin.site.register(KnowledgeBase)
admin.site.register(ChatSession)
admin.site.register(ChatMessage)