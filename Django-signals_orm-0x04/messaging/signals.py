from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model # Import get_user_model
from django.utils import timezone

from .models import Message, Notification, MessageHistory # Import your other models

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

# --- NEW SIGNAL: log_message_edit (pre_save for Message) ---
@receiver(pre_save, sender=Message, dispatch_uid="log_message_edit_history")
def log_message_edit(sender, instance, **kwargs):
    """
    Signal receiver that logs message content to MessageHistory before an update occurs.
    This runs BEFORE the Message instance is saved to the database.
    """
    # Check if the instance already exists in the database (i.e., it's an update, not a creation)
    # This is the key difference between creation and update in pre_save.
    if instance.pk: # instance.pk (primary key) will be set if it's an existing object
        try:
            # Retrieve the old version of the message from the database
            # .get_object_or_none() is not standard, so use .get() or .filter().first()
            # We use .get() but put it in a try-except just in case (e.g. race condition or object deleted)
            old_message = Message.objects.get(pk=instance.pk)

            # Compare the content to see if it actually changed
            if old_message.content != instance.content:
                # Content has changed, so log the old version
                MessageHistory.objects.create(
                    message=instance, # Link to the message being edited
                    old_content=old_message.content, # Save the content from BEFORE the edit
                    # We don't have request.user here directly in a signal,
                    # so edited_by would need to be set in a view (if applicable) or left null.
                    # For now, let's leave edited_by null, as the signal doesn't have request context.
                    # If you need edited_by, you'd usually pass it from a view context (more complex).
                )
                # Mark the message as edited
                instance.edited = True
                instance.edited_at = timezone.now() # Set edited timestamp

                print(f"DEBUG: Message {instance.id} content changed. Old content logged to history.")
            # If content didn't change, no need to log history or mark as edited
        except Message.DoesNotExist:
            # This case shouldn't happen often for an update, but good for robustness.
            # It means the object somehow vanished between being retrieved and pre_save.
            print(f"WARNING: Message {instance.id} not found in DB during pre_save, cannot log history.")
    # If instance.pk is None, it's a new message being created, so no history to log.