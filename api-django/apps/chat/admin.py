from django.contrib import admin

from apps.chat.models import ChatRoom, Message


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_group', 'name', 'friendship', 'created_by', 'created_at')
    list_filter = ('is_group',)
    raw_id_fields = ('friendship', 'created_by')
    filter_horizontal = ('participants',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'sender', 'sent_at', 'is_read')
    list_filter = ('is_read',)
    search_fields = ('content', 'sender__username')
    raw_id_fields = ('room', 'sender')
