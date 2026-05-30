"""
Users — Modelos
================
Modelo de usuario personalizado y vector de ADN musical para Encorely.

Patrones aplicados:
    - Herencia (POO): User extiende AbstractUser de Django
    - Enum (POO): ConcertMood usa TextChoices para tipificar el mood de concierto
    - Composición: MusicVibeVector está vinculado a User via OneToOneField

El User almacena la identidad y preferencias del usuario, mientras que
MusicVibeVector almacena el "ADN musical" calculado a partir de sus swipes.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


# ============================================
# ENUMS — Patrón Enum (POO)
# ============================================

class ConcertMood(models.TextChoices):
    """
    Enum que define el estilo de concierto preferido del usuario.

    Patrón POO — Enum/TextChoices:
    Encapsula las opciones válidas como constantes de clase,
    garantizando type-safety y legibilidad en el código.

    Uso: User.concert_mood = ConcertMood.MOSHPIT
    """
    MOSHPIT = 'moshpit', '🤘 Moshpit'
    FRONT_ROW = 'front_row', '🎤 Front Row'
    CHILLER = 'chiller', '😎 Chiller'
    VIP = 'vip', '🥂 VIP'


# ============================================
# MODELO USER — Herencia (POO)
# ============================================

class User(AbstractUser):
    """
    Modelo de usuario extendido para Encorely.

    Patrón POO — Herencia:
    Extiende AbstractUser de Django para mantener compatibilidad completa
    con el sistema de autenticación (login, permisos, sesiones) mientras
    agrega campos específicos de la plataforma musical.

    Campos extendidos:
        - display_name: Nombre visible en la app (diferente al username)
        - concert_mood: Estilo de concierto preferido (Enum ConcertMood)
        - city: Ciudad para filtrar eventos y matches cercanos
        - bio: Descripción breve del usuario
        - swipe_count: Contador de swipes realizados (se incrementa via Signal)
        - is_premium: Flag de usuario premium (futuras funcionalidades)

    Relaciones:
        - MusicVibeVector (OneToOne inverso): Vector de ADN musical
    """

    # ── Perfil ─────────────────────────────────────────
    display_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Nombre de perfil',
        help_text='Nombre que se muestra en la app. Si está vacío, se usa el username.'
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        default='',
        verbose_name='Biografía',
        help_text='Descripción breve sobre ti y tus gustos musicales.'
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Ciudad',
        help_text='Ciudad de residencia para filtrar eventos y matches cercanos.'
    )

    # ── Preferencia de concierto (Enum) ────────────────
    concert_mood = models.CharField(
        max_length=20,
        choices=ConcertMood.choices,
        default=ConcertMood.CHILLER,
        verbose_name='Mood de concierto',
        help_text='Tu estilo preferido en conciertos.'
    )

    # ── Gamificación ───────────────────────────────────
    swipe_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Swipes realizados',
        help_text='Cantidad de canciones evaluadas. Se necesitan 25 para desbloquear el Radar.'
    )
    is_premium = models.BooleanField(
        default=False,
        verbose_name='Usuario Premium',
        help_text='Indica si el usuario tiene acceso a funcionalidades premium.'
    )

    class Meta:
        db_table = 'encorely_users'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-date_joined']

    def __str__(self):
        """Representación legible: nombre de perfil o username + email."""
        name = self.display_name or self.username
        return f'{name} ({self.email})'

    @property
    def has_enough_swipes(self):
        """
        Verifica si el usuario completó el mínimo de 25 swipes
        requeridos para desbloquear el Radar de compatibilidad.
        """
        return self.swipe_count >= 25

    @property
    def swipe_progress_percent(self):
        """Porcentaje de progreso hacia los 25 swipes requeridos."""
        return min(round((self.swipe_count / 25) * 100), 100)


# ============================================
# MODELO MUSIC VIBE VECTOR — Composición (POO)
# ============================================

class MusicVibeVector(models.Model):
    """
    Vector de ADN musical del usuario.

    Patrón POO — Composición:
    Está vinculado a User via OneToOneField. Encapsula las dimensiones
    numéricas del perfil musical del usuario, calculadas a partir del
    promedio de audio features de sus swipes RIGHT.

    Los 4 campos numéricos (energy, danceability, valence, tempo) se
    utilizan en el algoritmo VibeCalculator (similitud del coseno)
    para calcular la compatibilidad entre usuarios.

    Campos:
        - user: Relación 1:1 con el modelo User
        - energy: Nivel de energía musical (0.0 a 1.0)
        - danceability: Qué tan bailable es su gusto (0.0 a 1.0)
        - valence: Positividad emocional de su música (0.0 a 1.0)
        - tempo: Tempo normalizado preferido (0.0 a 1.0)
        - top_genres: Lista de géneros más escuchados (JSON)
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='vibe_vector',
        verbose_name='Usuario'
    )

    # ── Dimensiones del vector (0.0 a 1.0) ────────────
    energy = models.FloatField(
        default=0.0,
        verbose_name='Energía',
        help_text='Nivel de energía musical promedio (0.0 = calmado, 1.0 = intenso).'
    )
    danceability = models.FloatField(
        default=0.0,
        verbose_name='Bailabilidad',
        help_text='Qué tan bailable es la música preferida (0.0 a 1.0).'
    )
    valence = models.FloatField(
        default=0.0,
        verbose_name='Valencia',
        help_text='Positividad emocional de la música (0.0 = triste, 1.0 = alegre).'
    )
    tempo = models.FloatField(
        default=0.0,
        verbose_name='Tempo',
        help_text='Tempo normalizado preferido (0.0 a 1.0).'
    )

    # ── Géneros top (JSON) ─────────────────────────────
    top_genres = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Géneros favoritos',
        help_text='Lista de géneros musicales más frecuentes en los swipes RIGHT.'
    )

    # ── Metadata ───────────────────────────────────────
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )

    class Meta:
        db_table = 'encorely_vibe_vectors'
        verbose_name = 'Vector de ADN Musical'
        verbose_name_plural = 'Vectores de ADN Musical'

    def __str__(self):
        return (
            f'VibeVector de {self.user.username} — '
            f'E:{self.energy:.2f} D:{self.danceability:.2f} '
            f'V:{self.valence:.2f} T:{self.tempo:.2f}'
        )

    def to_dict(self):
        """
        Retorna el vector como diccionario para uso en el
        algoritmo VibeCalculator (similitud del coseno).
        """
        return {
            'energy': self.energy,
            'danceability': self.danceability,
            'valence': self.valence,
            'tempo': self.tempo,
        }
