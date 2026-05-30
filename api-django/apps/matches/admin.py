from django.contrib import admin

from apps.matches.models import Friendship


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_source', 'user_target', 'compatibility_score', 'status', 'matched_at')
    list_filter = ('status',)
    search_fields = ('user_source__username', 'user_target__username')
    raw_id_fields = ('user_source', 'user_target')
