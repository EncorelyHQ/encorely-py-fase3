"""Permisos para relaciones Friendship — Patrón Authorization."""

from rest_framework import permissions


class IsFriendshipParticipant(permissions.BasePermission):
    """Solo los dos usuarios del par pueden acceder al objeto Friendship."""

    message = 'Solo los participantes de este match pueden realizar esta acción.'

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.id in (obj.user_source_id, obj.user_target_id)
