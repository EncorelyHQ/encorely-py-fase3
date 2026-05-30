"""
Matches — URL Configuration
=============================
Endpoints de compatibilidad y radar.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.matches.views import FriendshipViewSet

app_name = 'matches'

router = DefaultRouter()
router.register('matches', FriendshipViewSet, basename='friendship')

urlpatterns = [
    path('', include(router.urls)),
]
