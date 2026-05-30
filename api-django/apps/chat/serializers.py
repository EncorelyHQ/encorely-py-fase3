"""Serializers de salas y mensajes."""

from rest_framework import serializers

from apps.chat.models import ChatRoom, Message
from apps.users.models import User


class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'display_name')


class ChatRoomSerializer(serializers.ModelSerializer):
    """Sala con datos del otro participante respecto al usuario autenticado."""
    other_user = serializers.SerializerMethodField()
    friendship_status = serializers.CharField(source='friendship.status', read_only=True)

    class Meta:
        model = ChatRoom
        fields = ('id', 'friendship', 'friendship_status', 'other_user', 'created_at')
        read_only_fields = fields

    def get_other_user(self, obj):
        request = self.context.get('request')
        f = obj.friendship
        if request and request.user.is_authenticated:
            other = (
                f.user_target
                if f.user_source_id == request.user.id
                else f.user_source
            )
            return UserBriefSerializer(other).data
        return None


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
