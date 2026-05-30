"""
Unit tests for the MatchService logic.
Verifies compatibility calculations and suggestion filtering.
"""
import pytest
from django.contrib.auth import get_user_model
from apps.matches.services import MatchService
from apps.users.models import MusicVibeVector

User = get_user_model()

@pytest.mark.django_db
class TestMatchService:
    
    @pytest.fixture
    def users(self):
        u1 = User.objects.create_user(username='u1', email='u1@a.com')
        u2 = User.objects.create_user(username='u2', email='u2@a.com')
        
        # Crear vectores manualmente para el test
        MusicVibeVector.objects.create(user=u1, energy=0.8, danceability=0.8, valence=0.8, tempo=0.8)
        MusicVibeVector.objects.create(user=u2, energy=0.7, danceability=0.7, valence=0.7, tempo=0.7)
        
        return u1, u2

    def test_pair_score_calculation(self, users):
        u1, u2 = users
        score = MatchService.pair_score(u1, u2)
        # Cosine similarity de vectores proporcionales es 1.0
        assert score == pytest.approx(1.0)

    def test_compatibility_with_user_endpoint_logic(self, users):
        u1, u2 = users
        result = MatchService.compatibility_with_user(u1, u2.id)
        assert result['compatibility_score'] == pytest.approx(1.0)
        assert result['certified'] is True
