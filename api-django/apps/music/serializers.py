from rest_framework import serializers
from .models import Song, Swipe, SwipeType

class SongSerializer(serializers.ModelSerializer):
    """
    Serializer para lectura completa de canciones.
    """
    class Meta:
        model = Song
        fields = '__all__'


class SwipeCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para registrar un nuevo swipe.
    
    Validación: no permite swipes duplicados del mismo usuario a la misma canción.
    """
    class Meta:
        model = Swipe
        fields = ['song', 'type']

    def validate(self, data):
        user = self.context['request'].user
        song = data['song']
        
        if Swipe.objects.filter(user=user, song=song).exists():
            raise serializers.ValidationError("Ya has realizado un swipe a esta canción.")
        
        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class SwipeListSerializer(serializers.ModelSerializer):
    """
    Serializer para el historial de swipes con información anidada de la canción.
    """
    song = SongSerializer(read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Swipe
        fields = ['id', 'song', 'type', 'type_display', 'created_at']
