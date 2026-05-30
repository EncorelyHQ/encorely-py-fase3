from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Permite a los usuarios iniciar sesión utilizando su nombre de usuario o su correo electrónico.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
            
        try:
            # Buscar por username exacto o por email exacto
            user = User.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
        except User.DoesNotExist:
            # Evita ataques de timing (tiempo de respuesta)
            User().set_password(password)
            return None
            
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
