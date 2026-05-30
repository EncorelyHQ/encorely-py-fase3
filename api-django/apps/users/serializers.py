"""
Users — Serializers
===================
Serializadores para autenticación y perfiles de usuario.
Valida los datos de entrada y formatea las respuestas JSON.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import MusicVibeVector

from .services import UserService

User = get_user_model()


class MusicVibeVectorSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo MusicVibeVector.
    Solo lectura, ya que se actualiza automáticamente basado en los swipes.
    """
    class Meta:
        model = MusicVibeVector
        fields = ['energy', 'danceability', 'valence', 'tempo', 'top_genres']
        read_only_fields = fields


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer para registrar nuevos usuarios.
    Valida el email único y la confirmación de contraseña.
    """
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True, 
        required=True,
        style={'input_type': 'password'}
    )
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'display_name', 'concert_mood', 'city'
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está en uso.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        
        # Uso del Service Layer para la creación del usuario
        user = UserService.create_user(validated_data)
        
        # El vector se inicializa automáticamente vía Service o Signal
        UserService.generate_vibe_vector(user)
        
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para lectura del perfil completo del usuario.
    Incluye el vector de ADN musical anidado.
    """
    vibe_vector = MusicVibeVectorSerializer(read_only=True)
    has_enough_swipes = serializers.BooleanField(read_only=True)
    swipe_progress_percent = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'display_name', 'bio', 'city', 
            'concert_mood', 'swipe_count', 'is_premium', 
            'has_enough_swipes', 'swipe_progress_percent', 'vibe_vector'
        ]
        read_only_fields = ['id', 'username', 'email', 'swipe_count', 'is_premium']


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para la actualización parcial del perfil.
    Restringe qué campos pueden ser modificados por el usuario.
    """
    class Meta:
        model = User
        fields = ['display_name', 'bio', 'city', 'concert_mood']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom login serializer que incluye información básica del usuario
    además del token JWT.
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Agregar info básica al response de login para comodidad del frontend
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'display_name': self.user.display_name,
            'concert_mood': self.user.concert_mood,
            'has_enough_swipes': self.user.has_enough_swipes
        }
        return data
