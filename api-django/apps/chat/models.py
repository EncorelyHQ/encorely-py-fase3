"""
Chat — Modelos
===============
Salas de chat ligadas a una amistad ACEPTADA y mensajes.

Patrón: ChatRoom OneToOne con Friendship; mensajes con remitente y estado leído.
"""

from django.conf import settings
from django.db import models


class ChatRoom(models.Model):
    """Sala única asociada a un par de usuarios con match aceptado."""
    friendship = models.OneToOneField(
        'matches.Friendship',
        on_delete=models.CASCADE,
        related_name='chat_room',
        verbose_name='Amistad',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'encorely_chat_rooms'
        verbose_name = 'Sala de chat'
        verbose_name_plural = 'Salas de chat'

    def __str__(self) -> str:
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
