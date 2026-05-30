"""
Matches — Modelos
==================
Amistades y compatibilidad entre usuarios (Encorely).

Patrones: Enum (FriendshipStatus), constraints únicos para pares ordenados (POO/Django ORM).
"""

from django.conf import settings
from django.db import models
from django.db.models import F, Q


class FriendshipStatus(models.TextChoices):
    """Estado del vínculo entre dos usuarios."""
    SUGGESTED = 'suggested', 'Sugerido'
    PENDING = 'pending', 'Pendiente'
    ACCEPTED = 'accepted', 'Aceptado'
    BLOCKED = 'blocked', 'Bloqueado'


class Friendship(models.Model):
    """
    Relación entre dos usuarios y su nivel de compatibilidad musical.

    Los IDs se almacenan con user_source_id < user_target_id para garantizar
    un único registro por par (sin duplicar A-B y B-A).
    """
    user_source = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='friendships_as_source',
        verbose_name='Usuario (menor id)',
    )
    user_target = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='friendships_as_target',
        verbose_name='Usuario (mayor id)',
    )
    compatibility_score = models.FloatField(
        default=0.0,
        verbose_name='Score de compatibilidad',
        help_text='Similitud del coseno entre vectores musicales (0.0 a 1.0).',
    )
    status = models.CharField(
        max_length=20,
        choices=FriendshipStatus.choices,
        default=FriendshipStatus.SUGGESTED,
        verbose_name='Estado',
    )
    matched_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de match',
        help_text='Momento en que la relación pasó a ACCEPTED.',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'encorely_friendships'
        verbose_name = 'Amistad / Match'
        verbose_name_plural = 'Amistades / Matches'
        ordering = ['-updated_at']
        constraints = [
            models.CheckConstraint(
                condition=Q(user_source__lt=F('user_target')),
                name='friendship_source_lt_target',
            ),
            models.UniqueConstraint(
                fields=('user_source', 'user_target'),
                name='friendship_unique_ordered_pair',
            ),
        ]

    def __str__(self) -> str:
        return (
            f'{self.user_source_id} ↔ {self.user_target_id} '
            f'({self.status}) score={self.compatibility_score:.2f}'
        )
