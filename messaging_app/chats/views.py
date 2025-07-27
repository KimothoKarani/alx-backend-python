# messaging_app/chats/views.py

from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError # Import ValidationError

from .models import User, Conversation, Message
from .serializers import UserSerializer, ConversationSerializer, MessageSerializer
from .permissions import IsParticipant, IsMessageSenderOrConversationParticipant # Import custom permissions

# --- 1. Conversation ViewSet ---
class ConversationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows conversations to be viewed or edited.
    - Users can only list conversations they are a participant of.
    - Users can only retrieve, update, or delete conversations they are a participant of.
    - When creating, the requesting user is automatically added as a participant.
    """
    queryset = Conversation.objects.all().order_by('-created_at') # Base queryset for lookup
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipant] # Apply custom permission

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['participants__email', 'name'] # Search by conversation name too
    ordering_fields = ['created_at', 'updated_at'] # Add updated_at for ordering
    ordering = ['-updated_at']  # Default ordering

    def get_queryset(self):
        """
        Custom queryset to ensure a user only sees conversations they are a participant of.
        This handles the "list all conversations" (`GET /conversations/`) case.
        """
        # self.request.user is guaranteed to be authenticated due to IsAuthenticated
        return self.queryset.filter(participants=self.request.user).distinct()

    def perform_create(self, serializer):
        """
        Handles creation of a new conversation.
        Ensures the creating user is always a participant, even if not explicitly provided
        in `participant_ids` in the request.
        """
        # Get the list of participant User objects from the serializer's validated_data
        # serializer.validated_data['participant_ids'] is already a list of User instances
        # because of PrimaryKeyRelatedField in the serializer.
        participant_users = serializer.validated_data.get('participant_ids', [])

        # Ensure the creating user is part of the conversation
        if self.request.user not in participant_users:
            participant_users.append(self.request.user)

        # Save the conversation instance
        conversation = serializer.save()

        # Set the participants (this will handle both adding existing and the current user)
        # We need to set the participants *after* the conversation is created.
        conversation.participants.set(participant_users)

        # Optional: You might want to remove 'participant_ids' from validated_data
        # if the serializer's create method already attempts to use it directly,
        # but the current serializer's create method pops it, so it should be fine.


# --- 2. Message ViewSet ---
class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows messages to be viewed, created, or edited.
    - Users can only list/view messages if they are a participant of the conversation.
    - Users can only update/delete messages they sent.
    - When creating a message, the authenticated user is automatically set as the sender.
    - The conversation is linked via the URL's conversation_pk.
    """
    queryset = Message.objects.all().order_by('sent_at') # Base queryset for lookup
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsMessageSenderOrConversationParticipant]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['message_body', 'sender__email'] # Removed conversation__conversation_id as it's typically filtered by URL
    ordering_fields = ['sent_at']
    ordering = ['sent_at']  # Default message order

    def get_queryset(self):
        """
        Custom queryset to ensure messages are:
        1. Filtered by the parent conversation (from URL).
        2. Filtered to only include messages from conversations the current user is a participant of.
        """
        # This view is nested under conversations, so 'conversation_pk' will be in kwargs
        conversation_pk = self.kwargs.get('conversation_pk')

        if not conversation_pk:
            # If not nested, this means we're hitting /messages/{id}/ directly.
            # The IsMessageSenderOrConversationParticipant.has_object_permission will handle this.
            return super().get_queryset()

        # Ensure the conversation exists and the current user is a participant
        try:
            conversation = Conversation.objects.get(
                conversation_id=conversation_pk,
                participants=self.request.user # Filter by participant here for security
            )
        except Conversation.DoesNotExist:
            raise PermissionDenied("Conversation not found or you are not a participant.")

        # Return messages belonging to this specific conversation
        return self.queryset.filter(conversation=conversation)

    def perform_create(self, serializer):
        """
        Sets the sender of the message to the authenticated user.
        Links the message to the conversation specified in the URL.
        """
        # The conversation_pk is available from the URL due to nested routing.
        conversation_pk = self.kwargs.get('conversation_pk')

        if not conversation_pk:
            raise ValidationError({"conversation": "Conversation ID must be provided in the URL."})

        try:
            # Retrieve the conversation object. Ensure the current user is a participant.
            conversation = Conversation.objects.get(
                conversation_id=conversation_pk,
                participants=self.request.user
            )
        except Conversation.DoesNotExist:
            raise PermissionDenied("Conversation not found or you are not a participant.")

        # The serializer should already have 'conversation' set from 'conversation_id' PrimaryKeyRelatedField
        # We need to ensure the `serializer.validated_data['conversation']` matches `conversation` from URL.
        # This is implicitly handled if the `conversation_id` is passed correctly in the URL.
        # But we must ensure the `sender` and `conversation` are passed to save if they are `read_only_fields` in serializer.
        serializer.save(sender=self.request.user, conversation=conversation)