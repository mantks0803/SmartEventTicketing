from django.urls import path

from ai_agent.views import (
    ChatSessionListView,
    ChatSessionMessageListView,
    ChatView,
)


urlpatterns = [
    path(
        'chat/',
        ChatView.as_view(),
        name='ai-chat',
    ),
    path(
        'sessions/',
        ChatSessionListView.as_view(),
        name='ai-chat-sessions',
    ),
    path(
        'sessions/<int:session_id>/messages/',
        ChatSessionMessageListView.as_view(),
        name='ai-chat-session-messages',
    ),
]
