from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Configuración de la app Users — gestión de usuarios y perfiles."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'Usuarios'
