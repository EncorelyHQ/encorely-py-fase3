"""
Encorely — URL Configuration
=============================
Punto de entrada principal de URLs del proyecto.
Conecta las rutas de todas las apps y la documentación Swagger.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # ── Frontend Views ─────────────────────────────────
    path('', TemplateView.as_view(template_name='login.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='frontend-login'),
    path('register/', TemplateView.as_view(template_name='register.html'), name='frontend-register'),
    path('swipe/', TemplateView.as_view(template_name='swipe.html'), name='frontend-swipe'),
    path('radar/', TemplateView.as_view(template_name='radar.html'), name='frontend-radar'),
    path('events/', TemplateView.as_view(template_name='events.html'), name='frontend-events'),
    path('chat/', TemplateView.as_view(template_name='chat.html'), name='frontend-chat'),
    path('profile/', TemplateView.as_view(template_name='profile.html'), name='frontend-profile'),

    # ── Admin ──────────────────────────────────────────
    path('admin/', admin.site.urls),

    # ── API Endpoints ──────────────────────────────────
    path('api/auth/', include('apps.users.urls')),         # Auth: registro, login, perfil
    path('api/', include('apps.music.urls')),               # Songs & Swipes
    path('api/', include('apps.matches.urls')),             # Matches & Radar
    path('api/', include('apps.chat.urls')),                # Chat & Messages
    path('api/', include('apps.events.urls')),              # Events & Attendance

    # ── API Documentation (Swagger) ────────────────────
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
