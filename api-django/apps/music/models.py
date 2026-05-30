from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

# ============================================
# MIXINS — Patrón Herencia (POO)
# ============================================

class AudioFeaturesMixin(models.Model):
    """
    Mixin para encapsular las dimensiones de audio.
    
    Patrón POO — Mixin/Herencia:
    Provee campos comunes a canciones y vectores de afinidad, 
    permitiendo reutilización de código y consistencia en los datos.
    """
    energy = models.FloatField(default=0.0, verbose_name="Energía")
    danceability = models.FloatField(default=0.0, verbose_name="Bailabilidad")
    valence = models.FloatField(default=0.0, verbose_name="Valencia")
    tempo = models.FloatField(default=0.0, verbose_name="Tempo")

    class Meta:
        abstract = True


# ============================================
# ENUMS — Patrón Enum (POO)
# ============================================

class SwipeType(models.TextChoices):
    """
    Tipos de interacción swipe.
    """
    RIGHT = 'RIGHT', '➡️ Like'
    LEFT = 'LEFT', '⬅️ Dislike'


# ============================================
# MODELOS — Patrón POO
# ============================================

class Song(AudioFeaturesMixin):
    """
    Modelo representativo de una canción.
    
    Hereda atributos de AudioFeaturesMixin.
    """
    title = models.CharField(max_length=255, verbose_name="Título")
    artist_name = models.CharField(max_length=255, verbose_name="Artista")
    preview_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="Preview URL")
    image_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="Image URL")

    class Meta:
        db_table = 'encorely_songs'
        verbose_name = "Canción"
        verbose_name_plural = "Canciones"

    def __str__(self):
        return f"{self.title} - {self.artist_name}"


class Swipe(models.Model):
    """
    Registro de interacción entre un usuario y una canción.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='swipes',
        verbose_name="Usuario"
    )
    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name='swipes',
        verbose_name="Canción"
    )
    type = models.CharField(
        max_length=10,
        choices=SwipeType.choices,
        verbose_name="Tipo"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        db_table = 'encorely_swipes'
        verbose_name = "Swipe"
        verbose_name_plural = "Swipes"
        unique_together = ('user', 'song')

    def __str__(self):
        return f"{self.user.username} -> {self.song.title} ({self.type})"


# ============================================
# SIGNALS — Patrón Observer
# ============================================

@receiver(post_save, sender=Swipe)
def increment_user_swipe_count(sender, instance, created, **kwargs):
    """
    Signal que incrementa el contador de swipes del usuario automáticamente.
    
    Patrón Observer:
    Desacopla la lógica de gamificación de la creación del Swipe.
    """
    if created:
        from apps.users.services import UserService # Local import to avoid circular dependency
        user = instance.user
        user.swipe_count += 1
        user.save(update_fields=['swipe_count'])
        
        # Si el swipe es RIGHT, recalculamos el ADN musical (VibeVector)
        if instance.type == SwipeType.RIGHT:
            UserService.generate_vibe_vector(user)
