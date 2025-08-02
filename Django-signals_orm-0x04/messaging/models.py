import uuid

from django.contrib.auth.base_user import BaseUserManager
# messaging/models.py (at the top, for the User model)
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
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



# Adding a custom manager for better query methods
class MessageManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def with_related_data(self):
        return self.get_queryset().select_related('sender', 'receiver', 'parent_message') \
            .prefetch_related('replies')

    def get_threaded_messages(self, conversation_id=None, base_message_id=None):
        """
        Retrieves messages and organizes them into a threaded (tree-like) structure.
        Optimized using select_related and prefetch_related.

        :param conversation_id: Optional UUID to filter messages for a specific conversation.
                                (If you add a FK to Conversation model in Message)
        :param base_message_id: Optional UUID to fetch a specific message and all its replies.
        :return: A list of top-level Message instances, each having a 'replies_list' attribute
                 containing their nested replies.
        """
        # Fetch all relevant messages with optimized related data
        queryset = self.with_related_data()

        if conversation_id:
            # Assuming Message has a ForeignKey to a Conversation model
            # queryset = queryset.filter(conversation_id=conversation_id)
            # For current models, let's just get all messages for now if no Conversation FK
            pass

        if base_message_id:
            # If fetching a specific thread, get the base message and all its descendants.
            # This requires fetching ALL messages in the conversation/thread, then building the tree.
            # A true recursive query in Django ORM is complex without raw SQL.
            # Here, we fetch all, then build the tree.
            base_message = queryset.filter(id=base_message_id).first()
            if not base_message:
                return []

            # Fetch all messages that could potentially be part of this thread
            # (assuming they are in the same conversation for a real chat app)
            # For direct messages, this means all messages sent by/to sender/receiver of base_message
            thread_messages = queryset.filter(
                Q(sender=base_message.sender, receiver=base_message.receiver) |
                Q(sender=base_message.receiver, receiver=base_message.sender) |
                Q(parent_message=base_message) |
                Q(parent_message__parent_message=base_message)
                # Need more complex joins/filtering for deep recursion without raw SQL
            ).distinct().order_by('timestamp')  # Order them for tree building

            # Build the thread tree
            message_map = {msg.id: msg for msg in thread_messages}

            for msg_id, msg in message_map.items():
                msg.replies_list = []  # Add a list to hold child replies

            # Assign replies to their parents
            for msg_id, msg in message_map.items():
                if msg.parent_message_id and msg.parent_message_id in message_map:
                    message_map[msg.parent_message_id].replies_list.append(msg)

            # The top-level messages are those without a parent or whose parent is not in our fetched set
            top_level_messages = [
                msg for msg_id, msg in message_map.items()
                if msg.parent_message_id is None or msg.parent_message_id not in message_map
            ]

            # Sort replies within each parent
            for msg in message_map.values():
                msg.replies_list.sort(key=lambda x: x.timestamp)

            return sorted(top_level_messages, key=lambda x: x.timestamp)

        # If no specific base_message_id, return all top-level messages (no parent)
        # For a full chat conversation, you'd filter by conversation ID here
        return queryset.filter(parent_message__isnull=True)  # Returns messages that are not replies


# Make sure Message model uses this manager
# class Message(models.Model):
#    objects = MessageManager()
#    ...


# --- Custom Message Manager for Unread Messages ---
class UnreadMessagesManager(models.Manager):
    """
    Custom manager for the Message model to filter unread messages for a specific user.
    """
    def for_user(self, user):
        """
        Returns a queryset of unread messages for the given user (as receiver).
        Optimized with .only() to retrieve only necessary fields for display.
        """
        # Select related sender and parent_message to avoid N+1 queries later
        # Only retrieve essential fields using .only()
        # This is the optimization part.
        return self.get_queryset().select_related('sender', 'parent_message').filter(
            receiver=user,
            is_read=False
        ).only(
            'id', 'sender', 'receiver', 'content', 'timestamp', 'is_read', 'edited', 'edited_at', 'parent_message'
            # Must include all fields needed for display (sender, receiver, parent_message will be objects due to select_related)
            # and any fields directly accessed like content, timestamp, is_read, edited, edited_at.
            # Also include 'id' and 'parent_message' foreign key fields (even if nullable)
        ).order_by('-timestamp') # Order by most recent unread first



# --- Message Model (MODIFIED for threading) ---
class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        help_text="The user who sent this message."
    )

    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
        help_text="The user who is intended to receive this message."
    )

    # NEW: Self-referential ForeignKey for replies
    parent_message = models.ForeignKey(
        'self',  # Refers to the Message model itself
        on_delete=models.SET_NULL,  # If parent message is deleted, replies become top-level
        null=True,  # Allows a message to be a top-level message (no parent)
        blank=True,  # Allows forms to leave this field blank
        related_name='replies',  # Access replies to a message via message.replies.all()
        help_text="The message this message is a reply to."
    )

    # NEW: Link to Conversation (assuming messages belong to conversations for context)
    # This might have been implicitly handled by previous messaging_app structure,
    # but for a standalone chat, it's good to define it if replies are within a conversation.
    # If messages are just direct 1-1, you might omit this or use specific chat sessions.
    # For robust threading, a conversation ID is useful to group messages.
    # If this is part of your previous 'chats' app, this FK might already exist.
    # If not, let's add a basic one for context.
    # For simplicity, let's keep it simple direct messaging based on sender/receiver for now.
    # If you have a separate Conversation model you'd link to that.

    content = models.TextField(
        help_text="The body of the message."
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    is_read = models.BooleanField(default=False, help_text="Indicates if the receiver has read the message.")

    edited = models.BooleanField(default=False, help_text="Indicates if this message has been edited.")
    edited_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp of the last edit.")

    objects = MessageManager()
    unread_messages = UnreadMessagesManager()


    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ['timestamp']  # Order messages by time sent, ascending
        indexes = [
            models.Index(fields=['sender', 'receiver', 'timestamp']),
            models.Index(fields=['receiver', 'is_read', 'timestamp']),
            models.Index(fields=['parent_message', 'timestamp']),  # <-- NEW INDEX for replies
        ]

    def __str__(self):
        parent_info = f" (Reply to {self.parent_message.id})" if self.parent_message else ""
        return f"Message from {self.sender.username} to {self.receiver.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}{parent_info}"

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