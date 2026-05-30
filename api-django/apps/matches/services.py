"""
Matches — Service Layer
========================
Orquesta sugerencias y aceptación de matches usando VibeCalculator (Patrón Service Layer).
"""

from __future__ import annotations

from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone

from apps.music.algorithms import CERTIFIED_COMPATIBILITY_THRESHOLD, VibeCalculator
from apps.matches.models import Friendship, FriendshipStatus
from apps.users.models import User


class MatchService:
    """Reglas de negocio para compatibilidad y transición de estado de Friendship."""

    @staticmethod
    def pair_score(user_a: User, user_b: User) -> float:
        """Similitud 0..1 entre los vectores DNA de dos usuarios."""
        try:
            va = user_a.vibe_vector
            vb = user_b.vibe_vector
        except ObjectDoesNotExist:
            return 0.0
        return VibeCalculator.calculate(va.to_dict(), vb.to_dict())

    @staticmethod
    def suggest_matches(user: User) -> list[dict[str, Any]]:
        """
        Usuarios con score > umbral frente al usuario actual.
        Excluye matches ya aceptados / pendientes / bloqueados con ese par.
        """
        try:
            user.vibe_vector
        except ObjectDoesNotExist:
            return []

        blocked_states = (
            FriendshipStatus.ACCEPTED,
            FriendshipStatus.PENDING,
            FriendshipStatus.BLOCKED,
        )
        busy_pairs: set[int] = set()
        for row in Friendship.objects.filter(
            Q(user_source=user) | Q(user_target=user),
            status__in=blocked_states,
        ).only('user_source_id', 'user_target_id'):
            other_id = row.user_target_id if row.user_source_id == user.id else row.user_source_id
            busy_pairs.add(other_id)

        others = (
            User.objects.exclude(pk=user.pk)
            .select_related('vibe_vector')
            .filter(vibe_vector__isnull=False)
        )

        out: list[dict[str, Any]] = []
        for other in others:
            if other.id in busy_pairs:
                continue
            score = MatchService.pair_score(user, other)
            if score > CERTIFIED_COMPATIBILITY_THRESHOLD:
                out.append(
                    {
                        'user_id': other.id,
                        'username': other.username,
                        'display_name': other.display_name or other.username,
                        'city': other.city,
                        'compatibility_score': round(score, 4),
                    }
                )
        out.sort(key=lambda x: x['compatibility_score'], reverse=True)
        return out

    @staticmethod
    def accept_match(friendship_id: int, user: User) -> Friendship:
        """Pasa una Friendship PENDING a ACCEPTED (solo participantes)."""
        try:
            fs = Friendship.objects.get(pk=friendship_id)
        except Friendship.DoesNotExist as exc:
            raise ValueError('La solicitud de match no existe.') from exc

        if user.id not in (fs.user_source_id, fs.user_target_id):
            raise PermissionError('No participas en esta solicitud.')

        if fs.status != FriendshipStatus.PENDING:
            raise ValueError('Solo se pueden aceptar solicitudes pendientes.')

        fs.status = FriendshipStatus.ACCEPTED
        fs.matched_at = timezone.now()
        fs.save(update_fields=['status', 'matched_at', 'updated_at'])
        return fs

    @staticmethod
    def compatibility_with_user(request_user: User, other_id: int) -> dict[str, Any]:
        """Score en tiempo real frente a otro usuario por ID."""
        try:
            other = User.objects.select_related('vibe_vector').get(pk=other_id)
        except User.DoesNotExist as exc:
            raise ValueError('Usuario no encontrado.') from exc

        if other.id == request_user.id:
            raise ValueError('No puedes calcular compatibilidad contigo mismo.')

        score = MatchService.pair_score(request_user, other)
        return {
            'other_user_id': other.id,
            'username': other.username,
            'compatibility_score': round(score, 4),
            'certified': score > CERTIFIED_COMPATIBILITY_THRESHOLD,
        }
