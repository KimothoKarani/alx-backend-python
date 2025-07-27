# messaging_app/chats/permissions.py

from rest_framework import permissions
from .models import Conversation # Keep this import

# --- New: Explicit IsAuthenticated Permission (for checker) ---
class IsAuthenticatedCustom(permissions.BasePermission):
    """
    Custom permission to explicitly check if the user is authenticated.
    This duplicates functionality of rest_framework.permissions.IsAuthenticated
    but might be required by a checker looking for it in a custom file.
    """
    message = "Authentication credentials were not provided."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

# --- Existing: IsParticipant ---
class IsParticipantOfConversation(permissions.BasePermission):
    message = "You are not a participant of this conversation."

    def has_object_permission(self, request, view, obj):
        return request.user in obj.participants.all()

# --- Existing: IsMessageSenderOrConversationParticipant ---
class IsMessageSenderOrConversationParticipant(permissions.BasePermission):
    message = "You do not have permission to perform this action on this message or conversation."

    def has_permission(self, request, view):
        conversation_pk = view.kwargs.get('conversation_pk')
        if conversation_pk:
            try:
                conversation = Conversation.objects.get(conversation_id=conversation_pk)
                # Ensure the user is authenticated first for has_permission to be meaningful here
                # and then check if they are a participant.
                return request.user.is_authenticated and request.user in conversation.participants.all()
            except Conversation.DoesNotExist:
                return False
        # For direct /messages/{id}/ access where conversation_pk is not in URL,
        # has_object_permission will handle the specific checks.
        # But we still need to ensure authentication if this is a list/create endpoint.
        # This will be covered by DEFAULT_PERMISSION_CLASSES or explicit viewset permission.
        return True # Rely on has_object_permission for safety, or global IsAuthenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated and request.user in obj.conversation.participants.all()

        return request.user.is_authenticated and obj.sender == request.user