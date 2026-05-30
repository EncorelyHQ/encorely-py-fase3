from rest_framework import viewsets, generics, permissions, filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser, SAFE_METHODS
from .models import Song, Swipe
from .serializers import SongSerializer, SwipeCreateSerializer, SwipeListSerializer

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado: escritura para admin, lectura para todos.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class SongViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD de canciones.
    
    Accesible para lectura por todos, escritura solo por administradores.
    """
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None  # Deshabilitar paginación para cargar todas las canciones en el swipe
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'artist_name']
    ordering_fields = ['energy', 'danceability', 'valence', 'tempo']

    def get_queryset(self):
        """
        Añade filtrado personalizado y excluye canciones ya evaluadas por el usuario.
        """
        queryset = super().get_queryset()
        
        # Excluir canciones que el usuario ya deslizó (para no repetir)
        if self.request.user.is_authenticated:
            swiped_ids = Swipe.objects.filter(user=self.request.user).values_list('song_id', flat=True)
            queryset = queryset.exclude(id__in=swiped_ids)

        artist = self.request.query_params.get('artist')
        min_energy = self.request.query_params.get('min_energy')
        max_tempo = self.request.query_params.get('max_tempo')

        if artist:
            queryset = queryset.filter(artist_name__icontains=artist)
        if min_energy:
            queryset = queryset.filter(energy__gte=float(min_energy))
        if max_tempo:
            queryset = queryset.filter(tempo__lte=float(max_tempo))
            
        return queryset


class SwipeCreateView(generics.CreateAPIView):
    """
    Vista para registrar un nuevo swipe. Requiere autenticación JWT.
    """
    serializer_class = SwipeCreateSerializer
    permission_classes = [IsAuthenticated]


class MySwipesView(generics.ListAPIView):
    """
    Vista lista de los swipes del usuario autenticado.
    """
    serializer_class = SwipeListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Swipe.objects.select_related('song').filter(user=self.request.user).order_by('-created_at')
