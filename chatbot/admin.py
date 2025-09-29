from django.contrib import admin
from .models import *

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'content_type', 'is_processed', 'created_at')
    list_filter = ('is_processed', 'content_type', 'created_at')
    search_fields = ('title', 'user__email')
    readonly_fields = ('created_at',)

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'message_count')
    list_filter = ('created_at',)
    search_fields = ('title', 'user__email')
    readonly_fields = ('created_at',)

    def message_count(self, obj):
        return obj.message_set.count()
    message_count.short_description = 'Messages'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('get_conversation_title', 'role', 'truncated_content', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('conversation__title', 'content')
    readonly_fields = ('created_at',)

    def get_conversation_title(self, obj):
        return obj.conversation.title
    get_conversation_title.short_description = 'Conversation'
    get_conversation_title.admin_order_field = 'conversation__title'

    def truncated_content(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    truncated_content.short_description = 'Content'
