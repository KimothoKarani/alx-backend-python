from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Message, Notification, MessageHistory

# Register your models here.

# Get the custom User model
User = get_user_model() # Now 'User' refers to your custom user model

@admin.register(User) # You should register your custom User model too!
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('content', 'sender__email', 'receiver__email')
    list_filter = ('is_staff', 'is_active')
    # Add fields or fieldsets as desired

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'parent_message', 'content', 'timestamp', 'is_read', 'edited', 'edited_at') # <-- Add parent_message
    list_filter = ('timestamp', 'is_read', 'sender', 'receiver', 'edited', 'parent_message') # <-- Add parent_message to filter
    search_fields = ('content', 'sender__email', 'receiver__email', 'parent_message__content') # <-- Search by parent content
    date_hierarchy = 'timestamp'
    raw_id_fields = ('sender', 'receiver', 'parent_message') # Good for ForeignKey fields, especially self-referential

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'timestamp', 'is_read', 'message_link')
    list_filter = ('timestamp', 'is_read', 'user')
    search_fields = ('content', 'user__email')
    date_hierarchy = 'timestamp'

    def message_link(self, obj):
        if obj.message:
            return f"{obj.message.id} ({obj.message.content[:20]}...)"
        return "-"
    message_link.short_description = 'Related Message'

@admin.register(MessageHistory) # <-- Register MessageHistory
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ('message', 'old_content', 'edited_by', 'edited_at')
    list_filter = ('edited_at', 'message', 'edited_by')
    search_fields = ('old_content', 'message__content', 'edited_by__username')
    date_hierarchy = 'edited_at'