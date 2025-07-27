# messaging_app/chats/permissions.py

from rest_framework import permissions
from .models import Conversation  # Keep this import


# --- Existing: IsAuthenticatedCustom ---
class IsAuthenticatedCustom(permissions.BasePermission):
    message = "Authentication credentials were not provided."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


# --- Existing: IsParticipantOfConversation ---
class IsParticipantOfConversation(permissions.BasePermission):
    message = "You are not a participant of this conversation."

    def has_object_permission(self, request, view, obj):
        return request.user in obj.participants.all()


# --- MODIFIED: IsMessageSenderOrConversationParticipant ---
class IsMessageSenderOrConversationParticipant(permissions.BasePermission):
    message = "You do not have permission to perform this action on this message or conversation."

    def has_permission(self, request, view):
        conversation_pk = view.kwargs.get('conversation_pk')
        if conversation_pk:
            try:
                conversation = Conversation.objects.get(conversation_id=conversation_pk)
                return request.user.is_authenticated and request.user in conversation.participants.all()
            except Conversation.DoesNotExist:
                return False
        return True

    def has_object_permission(self, request, view, obj):
        # Read operations (GET, HEAD, OPTIONS): Any authenticated participant of the conversation can view the message.
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated and request.user in obj.conversation.participants.all()

        # Check for specific write operations: PUT, PATCH, DELETE
        # Only the message sender can modify/delete their own message.
        # Ensure user is authenticated before checking ownership.
        if request.user.is_authenticated:
            if request.method == 'PUT' or request.method == 'PATCH':
                return obj.sender == request.user  # Only sender can update
            if request.method == 'DELETE':
                return obj.sender == request.user  # Only sender can delete

        # If none of the above conditions met, or user not authenticated for write ops
        return False