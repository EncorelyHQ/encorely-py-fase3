"""
Chat — Modelos
===============
Salas de chat. Soporta dos tipos:
  - Directa (1:1): ligada a una Friendship ACEPTADA (se crea por signal).
  - Grupo (N usuarios): creada manualmente con nombre y participantes.

En ambos casos `participants` es la fuente de verdad de quién pertenece a la sala.
"""

from django.conf import settings
from django.db import models


class ChatRoom(models.Model):
    """Sala de chat directa (ligada a una amistad) o de grupo (varios usuarios)."""
    friendship = models.OneToOneField(
        'matches.Friendship',
        on_delete=models.CASCADE,
        related_name='chat_room',
        null=True,
        blank=True,
        verbose_name='Amistad',
    )
    is_group = models.BooleanField(default=False, verbose_name='Es grupo')
    name = models.CharField(
        max_length=120, blank=True, default='', verbose_name='Nombre del grupo'
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='chat_rooms',
        blank=True,
        verbose_name='Participantes',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_chat_rooms',
        verbose_name='Creado por',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'encorely_chat_rooms'
        verbose_name = 'Sala de chat'
        verbose_name_plural = 'Salas de chat'

    def __str__(self) -> str:
        if self.is_group:
            return f'Grupo «{self.name}» (#{self.pk})'
        return f'Chat {self.friendship_id}'


class Message(models.Model):
    """Mensaje dentro de una sala de chat."""
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Sala',
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_messages_sent',
        verbose_name='Remitente',
    )
    content = models.TextField(verbose_name='Contenido')
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name='Enviado')
    is_read = models.BooleanField(default=False, verbose_name='Leído')

    class Meta:
        db_table = 'encorely_messages'
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'
        ordering = ['sent_at']

    def __str__(self) -> str:
        preview = (self.content[:40] + '…') if len(self.content) > 40 else self.content
        return f'{self.sender_id} @ {self.sent_at:%Y-%m-%d %H:%M}: {preview}'
