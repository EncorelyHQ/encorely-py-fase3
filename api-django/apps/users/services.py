from django.contrib.auth import get_user_model
from django.db.models import Avg
from .models import MusicVibeVector
from apps.music.models import Swipe, SwipeType

User = get_user_model()

class UserService:
    """
    Capa de servicio para la gestión de usuarios y su vector de ADN musical.
    
    Patrón Service Layer:
    Centraliza la lógica de negocio, desacoplándola de las vistas y serializadores.
    """

    @staticmethod
    def create_user(data: dict) -> User:
        """
        Encapsula la creación del usuario con el hashing de password.
        """
        return User.objects.create_user(**data)

    @staticmethod
    def generate_vibe_vector(user: User) -> MusicVibeVector:
        """
        Genera o actualiza el vector de ADN musical (MusicVibeVector) 
        basado en el promedio de audio features de sus swipes RIGHT.
        
        Patrón Factory:
        Encapsula la creación/actualización del objeto MusicVibeVector.
        """
        # Obtener los swipes RIGHT del usuario
        right_swipes = Swipe.objects.filter(user=user, type=SwipeType.RIGHT)
        
        # Calcular los promedios de las dimensiones de audio
        averages = right_swipes.aggregate(
            avg_energy=Avg('song__energy'),
            avg_danceability=Avg('song__danceability'),
            avg_valence=Avg('song__valence'),
            avg_tempo=Avg('song__tempo')
        )

        # Si no hay swipes, el vector se mantiene en 0.0 (o valores por defecto)
        vibe_data = {
            'energy': averages['avg_energy'] or 0.0,
            'danceability': averages['avg_danceability'] or 0.0,
            'valence': averages['avg_valence'] or 0.0,
            'tempo': averages['avg_tempo'] or 0.0
        }

        # Actualizar o crear el vector
        vector, created = MusicVibeVector.objects.update_or_create(
            user=user,
            defaults=vibe_data
        )
        
        return vector
