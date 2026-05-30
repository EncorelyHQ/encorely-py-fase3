"""Permisos de chat — solo participantes del Friendship ligado a la sala."""

from rest_framework import permissions


class IsChatParticipant(permissions.BasePermission):
    message = 'No eres participante de esta conversación.'

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        from apps.chat.models import ChatRoom

        if isinstance(obj, ChatRoom):
            f = obj.friendship
        else:
            # Message
            f = obj.room.friendship
        return request.user.id in (f.user_source_id, f.user_target_id)
