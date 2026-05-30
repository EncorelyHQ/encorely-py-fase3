"""Tests de integración: VibeCalculator, MatchService y signal ChatRoom."""

from django.test import TestCase

from apps.chat.models import ChatRoom
from apps.matches.models import Friendship, FriendshipStatus
from apps.matches.services import MatchService
from apps.music.algorithms import CERTIFIED_COMPATIBILITY_THRESHOLD, VibeCalculator
from apps.users.models import MusicVibeVector, User


class VibeCalculatorIntegrationTests(TestCase):
    def test_identical_vectors_high_score(self):
        v = {'energy': 0.8, 'danceability': 0.7, 'valence': 0.6, 'tempo': 0.75}
        s = VibeCalculator.calculate(v, v)
        self.assertGreater(s, CERTIFIED_COMPATIBILITY_THRESHOLD)

    def test_suggest_matches_only_above_threshold(self):
        u1 = User.objects.create_user(username='u1', email='u1@test.com', password='pw')
        u2 = User.objects.create_user(username='u2', email='u2@test.com', password='pw')
        MusicVibeVector.objects.create(
            user=u1, energy=0.9, danceability=0.9, valence=0.9, tempo=0.9
        )
        MusicVibeVector.objects.create(
            user=u2, energy=0.9, danceability=0.9, valence=0.9, tempo=0.9
        )
        out = MatchService.suggest_matches(u1)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]['user_id'], u2.id)
        self.assertGreater(out[0]['compatibility_score'], CERTIFIED_COMPATIBILITY_THRESHOLD)

    def test_chat_room_created_when_friendship_accepted(self):
        a = User.objects.create_user(username='a', email='a@test.com', password='pw')
        b = User.objects.create_user(username='b', email='b@test.com', password='pw')
        fs = Friendship.objects.create(
            user_source=a,
            user_target=b,
            compatibility_score=0.85,
            status=FriendshipStatus.PENDING,
        )
        self.assertFalse(ChatRoom.objects.filter(friendship=fs).exists())
        fs.status = FriendshipStatus.ACCEPTED
        fs.save()
        self.assertTrue(ChatRoom.objects.filter(friendship=fs).exists())
