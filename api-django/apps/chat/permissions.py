"""Permisos de chat — solo participantes de la sala (directa o de grupo)."""

from rest_framework import permissions


class IsChatParticipant(permissions.BasePermission):
    message = 'No eres participante de esta conversación.'

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        from apps.chat.models import ChatRoom

        room = obj if isinstance(obj, ChatRoom) else obj.room
        return room.participants.filter(pk=request.user.pk).exists()
