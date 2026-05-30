from django.apps import AppConfig


class MusicConfig(AppConfig):
    """Configuración de la app Music — canciones, swipes y algoritmos."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.music'
    verbose_name = 'Música'
