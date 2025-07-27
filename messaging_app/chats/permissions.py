# messaging_app/chats/permissions.py

from rest_framework import permissions


class IsParticipant(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to view/edit/delete it.
    This applies to Conversation detail views (`/conversations/{id}/`).
    """
    message = "You are not a participant of this conversation."

    def has_object_permission(self, request, view, obj):
        # obj here is a Conversation instance.
        return request.user in obj.participants.all()


class IsMessageSenderOrConversationParticipant(permissions.BasePermission):
    """
    Custom permission for messages:
    - Allows participants of the conversation to list/view messages.
    - Only allows the message sender to update/delete their own message.
    """
    message = "You do not have permission to perform this action on this message or conversation."

    def has_permission(self, request, view):
        # For list (GET /conversations/{conv_id}/messages/) and create (POST /conversations/{conv_id}/messages/)
        # The user must be authenticated (default permission) and a participant of the *parent conversation*.

        # Get the conversation ID from the URL kwargs (set by nested router)
        conversation_pk = view.kwargs.get('conversation_pk')
        if not conversation_pk:
            # If conversation_pk is not in kwargs, it's likely a direct message detail view (e.g., /messages/{id}/)
            # or a non-nested list view. In such cases, if has_object_permission isn't triggered,
            # we rely on default IsAuthenticated or other permissions.
            # For this specific permission (MessageListCreateAPIView, MessageDetailAPIView), we expect conversation_pk.
            return True  # Let has_object_permission handle it or subsequent logic

        try:
            conversation = view.queryset.model.objects.get(conversation_id=conversation_pk)
            # Check if the requesting user is a participant in the conversation
            return request.user in conversation.participants.all()
        except view.queryset.model.DoesNotExist:
            return False  # Conversation does not exist

    def has_object_permission(self, request, view, obj):
        # obj here is a Message instance.

        # Read operations (GET, HEAD, OPTIONS): Any participant of the conversation can view.
        if request.method in permissions.SAFE_METHODS:
            return request.user in obj.conversation.participants.all()

        # Write operations (PUT, PATCH, DELETE): Only the message sender can modify/delete their own message.
        return obj.sender == request.user