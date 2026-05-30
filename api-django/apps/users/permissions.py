from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado para permitir que solo los dueños de un perfil
    puedan editarlo o eliminarlo.
    
    Patrón Authorization:
    Encapsula la lógica de propiedad para proteger recursos individuales.
    """

    def has_object_permission(self, request, view, obj):
        # Permisos de lectura están permitidos para cualquier petición
        if request.method in permissions.SAFE_METHODS:
            return True

        # Permisos de escritura solo están permitidos si el usuario es el dueño
        return obj == request.user
