# messaging_app/chats/views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import User, Conversation, Message
from .serializers import UserSerializer, ConversationSerializer, MessageSerializer

# --- 1. Conversation ViewSet ---
class ConversationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows conversations to be viewed or edited.
    Supports:
    - GET /conversations/ : List all conversations.
    - POST /conversations/ : Create a new conversation.
                             Requires 'participant_ids' (list of user_id UUIDs) in the request body.
    - GET /conversations/{id}/ : Retrieve a specific conversation.
    - PUT /conversations/{id}/ : Update a specific conversation.
    - PATCH /conversations/{id}/ : Partially update a specific conversation.
    - DELETE /conversations/{id}/ : Delete a specific conversation.
    """
    queryset = Conversation.objects.all().order_by('-created_at')
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated] # Ensure only authenticated users can access

    # When creating a new conversation, the serializer's create method
    # already handles setting up the many-to-many 'participants'.
    # No custom perform_create needed here unless specific logic (e.g., current user as participant) is required.
    # For now, it expects 'participant_ids' in the request body.

# --- 2. Message ViewSet ---
class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows messages to be viewed, created, or edited.
    Supports:
    - GET /messages/ : List all messages.
    - POST /messages/ : Send a new message.
                         Requires 'message_body' and 'conversation_id' (UUID) in the request body.
                         The 'sender' will be automatically set to the authenticated user.
    - GET /messages/{id}/ : Retrieve a specific message.
    - PUT /messages/{id}/ : Update a specific message.
    - PATCH /messages/{id}/ : Partially update a specific message.
    - DELETE /messages/{id}/ : Delete a specific message.
    """
    queryset = Message.objects.all().order_by('sent_at')
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated] # Ensure only authenticated users can access

    # Override perform_create to automatically set the sender of the message
    # to the currently authenticated user.
    def perform_create(self, serializer):
        """
        Sets the sender of the message to the authenticated user before saving.
        The conversation is expected to be provided in the request data (conversation_id).
        """
        # serializer.save() will call the create method in MessageSerializer.
        # We pass the 'sender' object directly, which will be used by 'source='sender'' in the serializer.
        serializer.save(sender=self.request.user)

    # Optional: If you want to filter messages by conversation, you might modify get_queryset.
    # For instance, if the URL was /conversations/{conversation_id}/messages/
    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     conversation_id = self.kwargs.get('conversation_pk') # Assuming nested router provides 'conversation_pk'
    #     if conversation_id:
    #         queryset = queryset.filter(conversation__conversation_id=conversation_id)
    #     return queryset