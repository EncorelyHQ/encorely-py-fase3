"""
Matches — Vistas
================
FriendshipViewSet + acciones radar y compatibilidad.
"""

from django.db.models import Q
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.matches.models import Friendship
from apps.matches.permissions import IsFriendshipParticipant
from apps.matches.serializers import (
    FriendshipCreateSerializer,
    FriendshipSerializer,
    FriendshipUpdateSerializer,
)
from apps.matches.services import MatchService


class FriendshipViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    Matches y radar de compatibilidad.
    Rutas: /api/matches/, /api/matches/radar/, /api/matches/compatibility/<id>/
    """
    queryset = Friendship.objects.none()

    def get_queryset(self):
        u = self.request.user
        return (
            Friendship.objects.filter(Q(user_source=u) | Q(user_target=u))
            .select_related('user_source', 'user_target')
            .order_by('-updated_at')
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return FriendshipCreateSerializer
        if self.action in ('partial_update', 'update'):
            return FriendshipUpdateSerializer
        return FriendshipSerializer

    def get_permissions(self):
        if self.action in ('partial_update', 'update'):
            return [IsAuthenticated(), IsFriendshipParticipant()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        inst = ser.save()
        out = FriendshipSerializer(inst, context=self.get_serializer_context())
        return Response(out.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        inst = self.get_object()
        ser = self.get_serializer(inst, data=request.data, partial=partial)
        ser.is_valid(raise_exception=True)
        inst = ser.save()
        return Response(FriendshipSerializer(inst, context=self.get_serializer_context()).data)

    @action(detail=False, methods=['get'], url_path='radar')
    def radar(self, request):
        """Compatibles con score > 0.70; bloqueado si swipe_count < 25."""
        user = request.user
        if not user.has_enough_swipes:
            raise PermissionDenied(
                detail='Completa 25 evaluaciones en Sound-Swipe para desbloquear el Radar.'
            )
        data = MatchService.suggest_matches(user)
        return Response(
            {
                'count': len(data),
                'minimum_swipes_required': 25,
                'your_swipe_count': user.swipe_count,
                'suggestions': data,
            }
        )

    @action(
        detail=False,
        methods=['get'],
        url_path=r'compatibility/(?P<other_id>\d+)',
        url_name='compatibility',
    )
    def compatibility_check(self, request, other_id=None):
        """Score en tiempo real frente a otro usuario."""
        try:
            oid = int(other_id)
        except (TypeError, ValueError):
            raise ValidationError('other_id inválido.')
        try:
            payload = MatchService.compatibility_with_user(request.user, oid)
        except ValueError as e:
            raise ValidationError(str(e)) from e
        return Response(payload)
