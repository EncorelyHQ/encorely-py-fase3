"""
Chat — Signals (Observer)
==========================
Al pasar una Friendship a ACCEPTED se crea la sala de chat automáticamente.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.chat.models import ChatRoom
from apps.matches.models import Friendship, FriendshipStatus


@receiver(post_save, sender=Friendship)
def ensure_chat_room_on_accepted(sender, instance, **kwargs):
    """Patrón Observer: Friendship ACCEPTED → ChatRoom asociada."""
    if instance.status != FriendshipStatus.ACCEPTED:
        return
    ChatRoom.objects.get_or_create(friendship=instance)
