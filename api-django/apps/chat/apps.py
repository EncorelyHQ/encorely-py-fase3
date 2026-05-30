from django.apps import AppConfig


class ChatConfig(AppConfig):
    """Configuración de la app Chat — mensajería entre usuarios."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.chat'
    verbose_name = 'Chat'

    def ready(self) -> None:
        from apps.chat import signals  # noqa: F401 — registrar receivers

