"""
Events — Vistas
===============
CRUD de eventos, asistencia y listado de asistentes con compatibilidad.
"""

from django.utils.dateparse import parse_date
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.events.models import Event, EventAttendance
from apps.events.serializers import EventAttendeeSerializer, EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    """
    `/api/events/events/` — CRUD y acciones attend / attendees.
    Filtros query: city, artist, date_from
    """
    serializer_class = EventSerializer
    queryset = Event.objects.all().order_by('event_date')

    def get_queryset(self):
        qs = super().get_queryset()
        city = self.request.query_params.get('city')
        artist = self.request.query_params.get('artist') or self.request.query_params.get('artist_name')
        date_from = self.request.query_params.get('date_from')
        if city:
            qs = qs.filter(city__icontains=city.strip())
        if artist:
            qs = qs.filter(artist_name__icontains=artist.strip())
        if date_from:
            d = parse_date(date_from.strip())
            if d:
                qs = qs.filter(event_date__date__gte=d)
        return qs

    @action(detail=True, methods=['post'], url_path='attend')
    def attend(self, request, pk=None):
        """Registrar intención de asistencia (idempotente)."""
        event = self.get_object()
        has_ticket = bool(request.data.get('has_ticket', False))
        att, created = EventAttendance.objects.update_or_create(
            user=request.user,
            event=event,
            defaults={'has_ticket': has_ticket},
        )
        ser = EventAttendeeSerializer(att, context={'request': request})
        st = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(ser.data, status=st)

    @action(detail=True, methods=['get'], url_path='attendees')
    def attendees(self, request, pk=None):
        """Lista de asistentes; `is_compatible` vs el usuario autenticado."""
        event = self.get_object()
        rows = EventAttendance.objects.filter(event=event).select_related('user')
        ser = EventAttendeeSerializer(
            rows,
            many=True,
            context={'request': request},
        )
        return Response({'count': rows.count(), 'results': ser.data})
