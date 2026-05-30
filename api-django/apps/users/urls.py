"""
Users — URL Configuration
==========================
Endpoints de autenticación y gestión de usuarios.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView, 
    MeView, 
    CustomTokenObtainPairView,
    UserViewSet
)

app_name = 'users'

router = DefaultRouter()
router.register(r'management', UserViewSet, basename='user')

urlpatterns = [
    # ── Auth Endpoints (JWT) ───────────────────────────
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # ── Perfil de Usuario ──────────────────────────────
    path('me/', MeView.as_view(), name='me'),
    
    # ── CRUD de Usuarios ──────────────────────────────
    path('', include(router.urls)),
]
