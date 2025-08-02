from django.db import models

# --- Custom Message Manager for Unread Messages ---
class UnreadMessagesManager(models.Manager):
    """
    Custom manager for the Message model to filter unread messages for a specific user.
    """
    def unread_for_user(self, user):
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


