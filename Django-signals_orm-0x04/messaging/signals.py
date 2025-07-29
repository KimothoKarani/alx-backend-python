from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model # Import get_user_model
from .models import Message, Notification # Import your other models

# Get the User model dynamically
User = get_user_model()

@receiver(post_save, sender=Message, dispatch_uid="create_notification_on_message_save")
def create_notification(sender, instance, created, **kwargs):
    """
    This signal runs every time a Message is saved.
    If it's a new message, we create a notification for the receiver.
    """
    # Check if the message was newly created (not updated)
    if created:
        # Check if a notification for this user and message already exists (due to unique_together)
        # This helps prevent integrity errors if the signal somehow fires multiple times or during re-processing
        if not Notification.objects.filter(user=instance.receiver, message=instance).exists():
            Notification.objects.create(
                user=instance.receiver, # Corrected: Use 'receiver' as per Message model
                message=instance,
                content=f"New message from {instance.sender.get_full_name() or instance.sender.email}", # Corrected: Use 'content', and get full name
                is_read=False # Explicitly set is_read to False for a new notification
            )
            # You might add a print statement for debugging:
            print(f"DEBUG: Notification created for {instance.receiver.username} for message {instance.id}")
    # Else (if message was updated), we don't create a new notification.
