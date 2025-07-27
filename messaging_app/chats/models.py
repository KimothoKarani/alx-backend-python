import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

# User Model
class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    All fields are explicitly defined to match the specified names and constraints.
    """
    username = None #Remove username field

    # user_id (Primary Key, UUID, Indexed)
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)

    # first_name (VARCHAR, NOT NULL)
    # Overriding AbstractUser's first_name to ensure NOT NULL (blank=False)
    first_name = models.CharField(max_length=150, null=False, blank=False)

    # last_name (VARCHAR, NOT NULL)
    # Overriding AbstractUser's last_name to ensure NOT NULL (blank=False)
    last_name = models.CharField(max_length=150, null=False, blank=False)

    # email (VARCHAR, UNIQUE, NOT NULL)
    # Overriding AbstractUser's email to ensure UNIQUE and NOT NULL
    email = models.EmailField(
        unique=True,
        null=False,
        blank=False,
        verbose_name='email address',
        help_text='Required. Unique email address for the user.'
    )

    # password_hash (VARCHAR, NOT NULL)
    # Django's AbstractUser handles password hashing internally in its 'password' field.
    # While the specification names it 'password_hash', we use AbstractUser's 'password'
    # field which effectively stores the hash. We do NOT redefine 'password' or add 'password_hash'
    # as a separate field to avoid conflicts with Django's authentication system.
    # The 'password' field (provided by AbstractUser) will be used for this purpose.
    # password = models.CharField(_("password"), max_length=128) - this is inherited

    # phone_number (VARCHAR, NULL)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    # role (ENUM: 'guest', 'host', 'admin', NOT NULL)
    class RoleChoices(models.TextChoices):
        GUEST = 'guest', 'Guest'
        HOST = 'host', 'Host'
        ADMIN = 'admin', 'Admin'

    role = models.CharField(
        max_length=10,
        choices=RoleChoices.choices,
        default=RoleChoices.GUEST,
        null=False,
    )

    # created_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
    # Overriding AbstractUser's 'date_joined' or adding a separate field.
    # To strictly match the name 'created_at', we add it explicitly.
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()  # Set the custom manager

    # Configure AbstractUser to use 'email' as the username field for authentication
    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS are prompted when creating a user (e.g., via createsuperuser)
    # if USERNAME_FIELD is not in them. Since we defined first_name and last_name
    # as NOT NULL, they should be required.
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-created_at'] # Order by our custom created_at

        # Additional Indexing as per specification (email is automatically indexed if unique=True, but explicit for clarity)
        indexes = [
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return self.email

# Conversation Model
class Conversation(models.Model):
    """
    Model representing a conversation, tracking its participants.
    """
    # conversation_id (Primary Key, UUID, Indexed)
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)

    # ADD THIS LINE FOR THE 'name' FIELD
    name = models.CharField(max_length=255, blank=True, null=True, help_text="Optional name for the conversation")

    # participants_id (Foreign Key, references User(user_id))
    # In Django, a ManyToManyField is used for this relationship.
    # It automatically creates an intermediary table where the foreign keys
    # (conversation_id and user_id, representing participants_id conceptually) reside.
    # The field name in the model should be 'participants' for idiomatic Django.
    participants = models.ManyToManyField(
        User,
        related_name='conversations',
        help_text='Users involved in this conversation. Corresponds to participants_id in the join table.'
    )

    # created_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # <--- THIS LINE MUST BE HERE

    class Meta:
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"
        ordering = ['-updated_at']

    def __str__(self):
        # Update __str__ to include name if it exists, otherwise fall back to participants
        if self.name:
            return self.name
        participant_emails = ", ".join([user.email for user in self.participants.all()[:3]])
        return f"Conversation with: {participant_emails}"

# Message Model
class Message(models.Model):
    """
    Model representing a single message within a conversation.
    """
    # message_id (Primary Key, UUID, Indexed)
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)

    # sender_id (Foreign Key, references User(user_id))
    # In Django, a ForeignKey field is typically named after the related model (e.g., 'sender').
    # Django automatically appends '_id' to create the database column name (e.g., 'sender_id').
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        help_text='The user who sent this message. Corresponds to sender_id in the database.'
    )

    # conversation as defined in the shared schema attached to this project
    # This implies a Foreign Key to the Conversation model.
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text='The conversation this message belongs to.'
    )

    # message_body (TEXT, NOT NULL)
    message_body = models.TextField(
        null=False,
        help_text='The content of the message.'
    )

    # sent_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        # Order messages by time sent, ascending, within a conversation
        ordering = ['sent_at']
        # Adding an index for efficient message retrieval within a conversation
        indexes = [
            models.Index(fields=['conversation', 'sent_at']),
        ]

    def __str__(self):
        return f"Message from {self.sender.email} in Conversation {self.conversation.conversation_id} at {self.sent_at.strftime('%Y-%m-%d %H:%M')}"