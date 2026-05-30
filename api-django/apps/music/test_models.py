"""
Integration tests for Music models and signals.
Verifies that swipes correctly trigger DNA updates and counter increments.
"""
import pytest
from django.contrib.auth import get_user_model
from apps.music.models import Song, Swipe, SwipeType
from apps.users.models import MusicVibeVector

User = get_user_model()

@pytest.mark.django_db
class TestMusicLogic:
    
    @pytest.fixture
    def user(self):
        return User.objects.create_user(username='tester', email='test@test.com', password='password123')
        
    @pytest.fixture
    def song(self):
        return Song.objects.create(
            title='Test Song',
            artist_name='Test Artist',
            energy=0.5,
            danceability=0.5,
            valence=0.5,
            tempo=0.5
        )

    def test_swipe_increments_count(self, user, song):
        """Verifica que un swipe incremente el contador del usuario via signal"""
        assert user.swipe_count == 0
        Swipe.objects.create(user=user, song=song, type=SwipeType.LEFT)
        user.refresh_from_db()
        assert user.swipe_count == 1

    def test_right_swipe_updates_vibe_vector(self, user, song):
        """Verifica que un swipe RIGHT dispare la actualización del vector"""
        # El vector se crea al registrarse en el serializer, pero aquí lo creamos manualmente
        # si no existe, o dejamos que el signal lo maneje.
        # En el proyecto real, el Vector se crea en UserRegistrationSerializer.create
        
        Swipe.objects.create(user=user, song=song, type=SwipeType.RIGHT)
        
        # El signal en music/models.py llama a UserService.generate_vibe_vector
        vibe = MusicVibeVector.objects.get(user=user)
        assert vibe.energy == song.energy
        assert vibe.danceability == song.danceability
        assert vibe.valence == song.valence
        assert vibe.tempo == song.tempo

    def test_multiple_swipes_averaging(self, user, song):
        """Verifica que el vector sea el promedio de los swipes RIGHT"""
        song2 = Song.objects.create(
            title='Song 2', artist_name='Art 2',
            energy=1.0, danceability=1.0, valence=1.0, tempo=1.0
        )
        
        Swipe.objects.create(user=user, song=song, type=SwipeType.RIGHT)
        Swipe.objects.create(user=user, song=song2, type=SwipeType.RIGHT)
        
        vibe = MusicVibeVector.objects.get(user=user)
        assert vibe.energy == pytest.approx(0.75) # (0.5 + 1.0) / 2
        assert vibe.danceability == pytest.approx(0.75)
