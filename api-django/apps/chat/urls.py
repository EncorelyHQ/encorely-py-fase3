"""
Chat — URL Configuration
==========================
Endpoints de mensajería.
"""

from django.urls import path

from apps.chat.views import ChatRoomListView, MessageListCreateView, MessageReadView

app_name = 'chat'

urlpatterns = [
    path('chat/rooms/', ChatRoomListView.as_view(), name='room-list'),
    path(
        'chat/rooms/<int:room_id>/messages/',
        MessageListCreateView.as_view(),
        name='message-list-create',
    ),
    path(
        'chat/messages/<int:pk>/read/',
        MessageReadView.as_view(),
        name='message-read',
    ),
]
