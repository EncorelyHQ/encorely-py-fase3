"""
Matches — Serializers
=====================
Friendship: lectura, creación de solicitud y actualización (aceptar / rechazar).
"""

from django.utils import timezone
from rest_framework import serializers

from apps.matches.models import Friendship, FriendshipStatus
from apps.matches.services import MatchService
from apps.users.models import User


class UserBriefSerializer(serializers.ModelSerializer):
    """Resumen de usuario para listados de matches."""

    class Meta:
        model = User
        fields = ('id', 'username', 'display_name', 'city', 'swipe_count')


class FriendshipSerializer(serializers.ModelSerializer):
    """Lectura de Friendship con usuarios anidados."""
    user_source = UserBriefSerializer(read_only=True)
    user_target = UserBriefSerializer(read_only=True)

    class Meta:
        model = Friendship
        fields = (
            'id',
            'user_source',
            'user_target',
            'compatibility_score',
            'status',
            'matched_at',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields


class FriendshipCreateSerializer(serializers.Serializer):
    """Enviar solicitud de match a otro usuario (estado PENDING)."""
    other_user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='other_user', write_only=True
    )

    def validate(self, attrs):
        request = self.context['request']
        me = request.user
        other = attrs['other_user']
        if me.id == other.id:
            raise serializers.ValidationError('No puedes enviarte una solicitud a ti mismo.')
        a, b = (me, other) if me.id < other.id else (other, me)
        existing = Friendship.objects.filter(user_source=a, user_target=b).first()
        if existing and existing.status == FriendshipStatus.ACCEPTED:
            raise serializers.ValidationError('Ya tienes un match aceptado con este usuario.')
        score = MatchService.pair_score(me, other)
        if score <= 0.0:
            raise serializers.ValidationError(
                'Ambos usuarios necesitan un vector musical calculado para evaluar compatibilidad.'
            )
        attrs['_compatibility_score'] = score
        attrs['_me'] = me
        attrs['_other'] = other
        return attrs

    def create(self, validated_data):
        me = validated_data['_me']
        other = validated_data['_other']
        score = validated_data['_compatibility_score']
        a, b = (me, other) if me.id < other.id else (other, me)
        fs, created = Friendship.objects.update_or_create(
            user_source=a,
            user_target=b,
            defaults={
                'compatibility_score': score,
                'status': FriendshipStatus.PENDING,
                'matched_at': None,
            },
        )
        return fs


class FriendshipUpdateSerializer(serializers.ModelSerializer):
    """Aceptar (ACCEPTED) o rechazar (BLOCKED) una solicitud PENDING."""

    class Meta:
        model = Friendship
        fields = ('status',)

    def validate_status(self, value):
        if value not in (FriendshipStatus.ACCEPTED, FriendshipStatus.BLOCKED):
            raise serializers.ValidationError('Solo se permite aceptar o rechazar el match.')
        return value

    def update(self, instance, validated_data):
        request = self.context['request']
        user = request.user
        new_status = validated_data.get('status')
        if instance.status != FriendshipStatus.PENDING:
            raise serializers.ValidationError('Esta solicitud ya fue procesada.')

        if user.id not in (instance.user_source_id, instance.user_target_id):
            raise serializers.ValidationError('No participas en esta solicitud.')

        if new_status == FriendshipStatus.ACCEPTED:
            instance.status = FriendshipStatus.ACCEPTED
            instance.matched_at = timezone.now()
        else:
            instance.status = FriendshipStatus.BLOCKED
            instance.matched_at = None

        instance.save(update_fields=['status', 'matched_at', 'updated_at'])
        return instance
