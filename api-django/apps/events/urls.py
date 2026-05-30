"""
Events — URL Configuration
============================
Endpoints de eventos y asistencia.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.events.views import EventViewSet

app_name = 'events'

router = DefaultRouter()
router.register('events', EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
]
