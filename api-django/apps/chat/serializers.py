"""Serializers de salas y mensajes."""

from rest_framework import serializers

from apps.chat.models import ChatRoom, Message
from apps.users.models import User


class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'display_name')


class ChatRoomSerializer(serializers.ModelSerializer):
    """Sala directa o de grupo, con un título y el otro participante (si es 1:1)."""
    other_user = serializers.SerializerMethodField()
    participants = UserBriefSerializer(many=True, read_only=True)
    title = serializers.SerializerMethodField()
    friendship_status = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = (
            'id',
            'is_group',
            'name',
            'title',
            'friendship',
            'friendship_status',
            'other_user',
            'participants',
            'created_at',
        )
        read_only_fields = fields

    def _request_user(self):
        request = self.context.get('request')
        return request.user if request and request.user.is_authenticated else None

    def get_friendship_status(self, obj):
        return obj.friendship.status if obj.friendship_id else None

    def get_other_user(self, obj):
        # Solo aplica a salas directas (1:1).
        if obj.is_group or not obj.friendship_id:
            return None
        user = self._request_user()
        if not user:
            return None
        f = obj.friendship
        other = f.user_target if f.user_source_id == user.id else f.user_source
        return UserBriefSerializer(other).data

    def get_title(self, obj):
        if obj.is_group:
            return obj.name or f'Grupo #{obj.pk}'
        other = self.get_other_user(obj) or {}
        return other.get('display_name') or other.get('username') or 'Chat'


class ChatRoomCreateSerializer(serializers.Serializer):
    """Crea una sala de grupo con un nombre y una lista de participantes."""
    name = serializers.CharField(max_length=120)
    participant_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, write_only=True
    )

    def validate_participant_ids(self, value):
        if not value:
            raise serializers.ValidationError('Agrega al menos un participante al grupo.')
        return value

    def create(self, validated_data):
        creator = self.context['request'].user
        members = {u.id: u for u in validated_data['participant_ids']}
        members[creator.id] = creator  # el creador siempre pertenece al grupo

        room = ChatRoom.objects.create(
            is_group=True,
            name=validated_data['name'],
            created_by=creator,
        )
        room.participants.set(list(members.values()))
        return room


class MessageSerializer(serializers.ModelSerializer):
    sender = UserBriefSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'room', 'sender', 'content', 'sent_at', 'is_read')
        read_only_fields = ('id', 'sender', 'sent_at', 'is_read')


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('content',)


class MessageReadSerializer(serializers.ModelSerializer):
    """Marcar mensaje como leído."""

    class Meta:
        model = Message
        fields = ('is_read',)

    def update(self, instance, validated_data):
        instance.is_read = validated_data.get('is_read', True)
        instance.save(update_fields=['is_read'])
        return instance
