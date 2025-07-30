import uuid

from django.contrib.auth.base_user import BaseUserManager
# messaging/models.py (at the top, for the User model)
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _  # For verbose names


class CustomUserManager(BaseUserManager):
    # We need to override _create_user because the default implementation
    # tries to pass 'username' to the model's __init__, which we've removed.
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)  # Now 'email' is explicitly passed
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    # Remove username field as we are using email for authentication
    username = None

    # Override email field for validation and verbose name
    email = models.EmailField(
        _('email address'),
        unique=True,
        blank=False,
        null=False,
        help_text='Required. Unique email address for the user.'
    )

    first_name = models.CharField(_('first name'), max_length=150, blank=False,
                                  null=False)  # Increased max_length, added verbose_name, non-nullable
    last_name = models.CharField(_('last name'), max_length=150, blank=False,
                                 null=False)  # Increased max_length, added verbose_name, non-nullable

    # Specify email as the USERNAME_FIELD for authentication
    USERNAME_FIELD = 'email'
    # These fields will be prompted when creating a superuser if not already set by USERNAME_FIELD
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering=['last_name', 'first_name']

    def __str__(self):
        # A more user-friendly representation
        return self.get_full_name() or self.email

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.email  # Fallback to email if name isn't set


class Message(models.Model):  # Renamed to singular 'Message'
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          editable=False)  # Use UUID for consistency with previous project

    # Use ForeignKey to link to the User model
    sender = models.ForeignKey(
        User,  # Link to our custom User model
        on_delete=models.CASCADE,  # If sender user is deleted, delete their messages
        related_name='sent_messages',  # Access messages sent by a user via user.sent_messages.all()
        help_text="The user who sent this message."
    )

    receiver = models.ForeignKey(
        User,  # Link to our custom User model
        on_delete=models.CASCADE,  # If receiver user is deleted, delete messages addressed to them
        related_name='received_messages',  # Access messages received by a user via user.received_messages.all()
        help_text="The user who is intended to receive this message."
    )

    content = models.TextField(
        help_text="The body of the message."
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    # Optional: Add an 'is_read' status, very common for messages
    is_read = models.BooleanField(default=False, help_text="Indicates if the receiver has read the message.")

    edited = models.BooleanField(default=False, help_text="Indicates if this message has been edited.")
    edited_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp of the last edit.")


    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ['timestamp']  # Order messages by time sent, ascending (most common for chats)
        # Adding an index for efficient message retrieval for conversations/users
        indexes = [
            models.Index(fields=['sender', 'receiver', 'timestamp']),
            models.Index(fields=['receiver', 'is_read', 'timestamp']),  # For unread messages for a user
        ]

    def __str__(self):
        # A more descriptive string representation including sender and receiver usernames
        # models.py
        return f"Message from {self.sender.email} to {self.receiver.email} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to the Message model (singular)
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        null=True,  # Allow notifications not directly linked to a message (e.g. system alerts)
        blank=True,  # Allow notifications not directly linked to a message
        related_name='notifications',
        help_text="The message that triggered this notification (optional)."
    )

    # The user to whom this notification is addressed
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',  # Access notifications for a user via user.notifications.all()
        help_text="The user to whom this notification is addressed."
    )

    content = models.TextField(  # Add content for the notification text itself
        help_text="The text content of the notification."
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    is_read = models.BooleanField(default=False, help_text="Indicates if the user has read this notification.")

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-timestamp']  # Order notifications by most recent first
        # Consider if unique_together is absolutely necessary. For a "new message" notification,
        # it might be, to prevent duplicate notifications for the same message to the same user.
        # If a user can receive multiple notifications for one message (e.g., new, then read receipt),
        # remove unique_together. Sticking with it for now.
        unique_together = ['user', 'message']

    def __str__(self):
        status = "Read" if self.is_read else "Unread"
        # Display the notification content and status
        return f"Notification for {self.user.username}: '{self.content[:50]}...' ({status})"


# --- NEW MODEL: MessageHistory ---
class MessageHistory(models.Model):
    """
    Stores historical versions of a message's content after it has been edited.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to the original Message
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,  # If the original message is deleted, delete its history
        related_name='history',
        help_text="The original message this history entry belongs to."
    )

    old_content = models.TextField(
        help_text="The content of the message before the edit."
    )

    edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,  # If the user who edited is deleted, keep the history but set to null
        null=True,
        blank=True,
        related_name='edited_messages_history',
        help_text="The user who performed this edit (optional)."
    )

    edited_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when this version was saved.")

    class Meta:
        verbose_name = "Message History"
        verbose_name_plural = "Message History"
        ordering = ['edited_at']  # Order history chronologically

    def __str__(self):
        editor = self.edited_by.username if self.edited_by else "Unknown"
        return f"History for Message {self.message.id} by {editor} at {self.edited_at.strftime('%Y-%m-%d %H:%M')}"