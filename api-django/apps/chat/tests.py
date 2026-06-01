"""
Chat — Tests
============
Cubre la creación de grupos, los permisos por participante y la sala directa
que se crea automáticamente al aceptar un match.
"""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.chat.models import ChatRoom
from apps.matches.models import Friendship, FriendshipStatus

User = get_user_model()


class GroupChatTests(APITestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username='alice', password='x', email='a@x.com')
        self.bob = User.objects.create_user(username='bob', password='x', email='b@x.com')
        self.carol = User.objects.create_user(username='carol', password='x', email='c@x.com')

    def test_create_group_includes_creator_and_members(self):
        self.client.force_authenticate(self.alice)
        resp = self.client.post(
            '/api/chat/rooms/',
            {'name': 'Plan concierto', 'participant_ids': [self.bob.id]},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(resp.data['is_group'])
        self.assertEqual(resp.data['title'], 'Plan concierto')
        ids = {p['id'] for p in resp.data['participants']}
        self.assertEqual(ids, {self.alice.id, self.bob.id})

    def test_create_group_requires_participants(self):
        self.client.force_authenticate(self.alice)
        resp = self.client.post(
            '/api/chat/rooms/',
            {'name': 'Vacío', 'participant_ids': []},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_member_can_post_message(self):
        self.client.force_authenticate(self.alice)
        room = self.client.post(
            '/api/chat/rooms/',
            {'name': 'Grupo', 'participant_ids': [self.bob.id]},
            format='json',
        ).data
        resp = self.client.post(
            f'/api/chat/rooms/{room["id"]}/messages/',
            {'content': 'hola grupo'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['content'], 'hola grupo')

    def test_non_member_cannot_read_group(self):
        self.client.force_authenticate(self.alice)
        room = self.client.post(
            '/api/chat/rooms/',
            {'name': 'Grupo privado', 'participant_ids': [self.bob.id]},
            format='json',
        ).data
        # Carol no es miembro.
        self.client.force_authenticate(self.carol)
        resp = self.client.get(f'/api/chat/rooms/{room["id"]}/messages/')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_group_only_lists_for_its_members(self):
        self.client.force_authenticate(self.alice)
        self.client.post(
            '/api/chat/rooms/',
            {'name': 'Solo A y B', 'participant_ids': [self.bob.id]},
            format='json',
        )
        # Carol no debe ver el grupo en su listado.
        self.client.force_authenticate(self.carol)
        resp = self.client.get('/api/chat/rooms/')
        results = resp.data.get('results', resp.data)
        self.assertEqual(len(results), 0)


class DirectRoomSignalTests(APITestCase):
    def test_accepted_friendship_creates_room_with_participants(self):
        a = User.objects.create_user(username='u1', password='x', email='u1@x.com')
        b = User.objects.create_user(username='u2', password='x', email='u2@x.com')
        source, target = (a, b) if a.id < b.id else (b, a)

        friendship = Friendship.objects.create(
            user_source=source,
            user_target=target,
            status=FriendshipStatus.ACCEPTED,
            compatibility_score=0.9,
        )
        room = ChatRoom.objects.get(friendship=friendship)
        self.assertFalse(room.is_group)
        self.assertEqual(
            {u.id for u in room.participants.all()},
            {a.id, b.id},
        )
