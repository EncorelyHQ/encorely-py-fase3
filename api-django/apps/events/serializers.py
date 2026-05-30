"""Serializers de eventos y asistentes."""

from rest_framework import serializers

from apps.events.models import Event, EventAttendance
from apps.matches.services import MatchService


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            'id',
            'title',
            'artist_name',
            'venue_name',
            'event_date',
            'city',
            'affiliate_url',
            'created_at',
        )
        read_only_fields = ('id', 'created_at')


class EventAttendeeSerializer(serializers.ModelSerializer):
    """Usuario asistente con flag de compatibilidad musical con quien consulta."""
    user = serializers.SerializerMethodField()
    is_compatible = serializers.SerializerMethodField()

    class Meta:
        model = EventAttendance
        fields = ('id', 'user', 'has_ticket', 'created_at', 'is_compatible')
        read_only_fields = fields

    def get_user(self, obj):
        u = obj.user
        return {
            'id': u.id,
            'username': u.username,
            'display_name': u.display_name or u.username,
            'city': u.city,
        }

    def get_is_compatible(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        try:
            score = MatchService.pair_score(request.user, obj.user)
        except Exception:
            return False
        from apps.music.algorithms import CERTIFIED_COMPATIBILITY_THRESHOLD

        return score > CERTIFIED_COMPATIBILITY_THRESHOLD
