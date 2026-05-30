"""
Chat — Vistas
=============
Listado de salas, mensajes por sala y marcar lectura.
"""

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView, ListCreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.chat.models import ChatRoom, Message
from apps.chat.permissions import IsChatParticipant
from apps.chat.serializers import (
    ChatRoomSerializer,
    MessageCreateSerializer,
    MessageReadSerializer,
    MessageSerializer,
)


class ChatRoomListView(ListAPIView):
    """GET — salas de chat del usuario (participante en el Friendship)."""
    permission_classes = [IsAuthenticated]
    serializer_class = ChatRoomSerializer

    def get_queryset(self):
        u = self.request.user
        return (
            ChatRoom.objects.filter(
                Q(friendship__user_source=u) | Q(friendship__user_target=u)
            )
            .select_related('friendship', 'friendship__user_source', 'friendship__user_target')
            .order_by('-created_at')
        )


class MessageListCreateView(ListCreateAPIView):
    """GET/POST — mensajes de una sala (solo participantes)."""
    permission_classes = [IsAuthenticated, IsChatParticipant]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MessageCreateSerializer
        return MessageSerializer

    def get_room(self):
        return get_object_or_404(
            ChatRoom.objects.select_related('friendship'),
            pk=self.kwargs['room_id'],
        )

    def check_permissions(self, request):
        super().check_permissions(request)
        room = self.get_room()
        self.check_object_permissions(request, room)

    def get_queryset(self):
        room_id = self.kwargs['room_id']
        return (
            Message.objects.filter(room_id=room_id)
            .select_related('sender')
            .order_by('sent_at')
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        room = self.get_room()
        msg = Message.objects.create(
            room=room,
            sender=request.user,
            content=serializer.validated_data['content'],
        )
        out = MessageSerializer(msg, context=self.get_serializer_context())
        return Response(out.data, status=status.HTTP_201_CREATED)


class MessageReadView(UpdateAPIView):
    """PATCH — marcar mensaje como leído (solo participantes)."""
    permission_classes = [IsAuthenticated, IsChatParticipant]
    serializer_class = MessageReadSerializer
    http_method_names = ['patch', 'options', 'head']

    def get_queryset(self):
        u = self.request.user
        return Message.objects.filter(
            Q(room__friendship__user_source=u) | Q(room__friendship__user_target=u)
        ).select_related('room__friendship')
