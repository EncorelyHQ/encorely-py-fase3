from django.contrib import admin

from apps.events.models import Event, EventAttendance


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist_name', 'venue_name', 'event_date', 'city')
    list_filter = ('city',)
    search_fields = ('title', 'artist_name', 'venue_name', 'city')


@admin.register(EventAttendance)
class EventAttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'event', 'has_ticket', 'created_at')
    list_filter = ('has_ticket',)
    raw_id_fields = ('user', 'event')
