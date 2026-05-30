from django.contrib import admin
from .models import Song, Swipe

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist_name', 'energy', 'danceability', 'valence', 'tempo')
    search_fields = ('title', 'artist_name')
    list_filter = ('artist_name',)

@admin.register(Swipe)
class SwipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'song', 'type', 'created_at')
    search_fields = ('user__username', 'song__title')
    list_filter = ('type', 'created_at')
