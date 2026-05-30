"""Rellena `participants` en las salas directas existentes a partir de su Friendship."""

from django.db import migrations


def backfill_participants(apps, schema_editor):
    ChatRoom = apps.get_model('chat', 'ChatRoom')
    for room in ChatRoom.objects.filter(friendship__isnull=False):
        f = room.friendship
        room.participants.add(f.user_source_id, f.user_target_id)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_chatroom_created_by_chatroom_is_group_chatroom_name_and_more'),
    ]

    operations = [
        migrations.RunPython(backfill_participants, noop),
    ]
