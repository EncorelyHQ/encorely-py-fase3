"""
Events — Modelos
=================
Conciertos y asistencia de usuarios.
"""

from django.conf import settings
from django.db import models


class Event(models.Model):
    """Concierto o evento musical publicado en la plataforma."""
    title = models.CharField(max_length=255, verbose_name='Título')
    artist_name = models.CharField(max_length=255, verbose_name='Artista')
    venue_name = models.CharField(max_length=255, verbose_name='Lugar')
    event_date = models.DateTimeField(verbose_name='Fecha del evento')
    city = models.CharField(max_length=100, verbose_name='Ciudad')
    affiliate_url = models.URLField(blank=True, default='', verbose_name='URL afiliado')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'encorely_events'
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['event_date']

    def __str__(self) -> str:
        return f'{self.title} — {self.city}'


class EventAttendance(models.Model):
    """Registro de que un usuario planea asistir a un evento."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='event_attendances',
        verbose_name='Usuario',
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name='Evento',
    )
    has_ticket = models.BooleanField(default=False, verbose_name='Tiene entrada')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'encorely_event_attendance'
        verbose_name = 'Asistencia a evento'
        verbose_name_plural = 'Asistencias a eventos'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'event'),
                name='event_attendance_unique_user_event',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.user_id} → {self.event_id} (ticket={self.has_ticket})'
