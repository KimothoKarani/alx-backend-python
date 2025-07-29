from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Message, Notification

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
    list_display = ('sender', 'receiver', 'content', 'timestamp', 'is_read')
    list_filter = ('timestamp', 'is_read', 'sender', 'receiver')
    search_fields = ('content', 'sender__username', 'receiver__username')
    date_hierarchy = 'timestamp' # Adds navigation by date

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'timestamp', 'is_read', 'message_link')
    list_filter = ('timestamp', 'is_read', 'user')
    search_fields = ('content', 'user__username')
    date_hierarchy = 'timestamp'

    def message_link(self, obj):
        if obj.message:
            return f"{obj.message.id} ({obj.message.content[:20]}...)"
        return "-"
    message_link.short_description = 'Related Message'