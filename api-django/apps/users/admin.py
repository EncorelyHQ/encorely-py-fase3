"""
Users — Admin
=============
Configuración del panel de administración de Django para los
modelos de la app users.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, MusicVibeVector


@admin.register(MusicVibeVector)
class MusicVibeVectorAdmin(admin.ModelAdmin):
    """
    Panel de administración para los vectores de ADN musical.
    """
    list_display = ('user', 'energy', 'danceability', 'valence', 'tempo', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('updated_at',)
    list_filter = ('user__is_premium',)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Panel de administración extendido para el usuario de Encorely.
    Incorpora los campos adicionales del modelo User.
    """
    list_display = ('username', 'email', 'display_name', 'concert_mood', 'swipe_count', 'is_premium', 'is_staff')
    list_filter = ('concert_mood', 'is_premium', 'city', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'display_name', 'city')
    
    # Añadimos la sección "Encorely Profile" al formulario de edición del admin
    fieldsets = UserAdmin.fieldsets + (
        ('Encorely Profile', {
            'fields': (
                'display_name', 
                'bio', 
                'city', 
                'concert_mood', 
                'swipe_count', 
                'is_premium'
            )
        }),
    )
