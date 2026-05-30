from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    CustomTokenObtainPairSerializer,
    MusicVibeVectorSerializer
)

User = get_user_model()


class RegisterView(CreateAPIView):
    """
    Vista para el registro de nuevos usuarios.
    Endpoint: POST /api/auth/register/
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer


class MeView(RetrieveUpdateAPIView):
    """
    Vista para obtener o actualizar el perfil del usuario autenticado.
    Endpoint: GET, PUT, PATCH /api/auth/me/
    Requiere token JWT en el header: Authorization: Bearer <token>
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        # Siempre retorna el usuario que hace la petición
        return self.request.user

    def get_serializer_class(self):
        # Diferente serializer si es lectura o escritura
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserProfileSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD completo de usuarios.
    
    Acciones:
        - list: Listado de usuarios (público)
        - retrieve: Detalle de usuario (público)
        - update/partial_update: Solo dueño
        - destroy: Solo dueño
    """
    queryset = User.objects.all()
    permission_classes = [IsOwnerOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserProfileSerializer

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def vibe(self, request, pk=None):
        """
        Retorna el vector de ADN musical del usuario.
        Endpoint: GET /api/users/{id}/vibe/
        """
        user = self.get_object()
        vibe_vector = getattr(user, 'vibe_vector', None)
        
        if not vibe_vector:
            return Response(
                {"error": "Este usuario aún no tiene un vector de afinidad musical."},
                status=status.HTTP_404_NOT_FOUND
            )
            
        serializer = MusicVibeVectorSerializer(vibe_vector)
        return Response(serializer.data)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vista para login JWT que devuelve token + info del usuario.
    Endpoint: POST /api/auth/login/
    """
    serializer_class = CustomTokenObtainPairSerializer
