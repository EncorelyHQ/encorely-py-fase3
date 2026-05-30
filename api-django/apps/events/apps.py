from django.apps import AppConfig


class EventsConfig(AppConfig):
    """Configuración de la app Events — conciertos y asistencia."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.events'
    verbose_name = 'Eventos'
