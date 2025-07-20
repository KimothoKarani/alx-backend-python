from rest_framework import viewsets, status, filters
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
    permission_classes = [IsAuthenticated]

    # ✅ Enable filtering and searching on participants' email
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['participants__email']
    ordering_fields = ['created_at']
    ordering = ['-created_at']  # Default ordering


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
    permission_classes = [IsAuthenticated]

    # ✅ Add filter support for message body, sender email, or conversation ID
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['message_body', 'sender__email', 'conversation__conversation_id']
    ordering_fields = ['sent_at']
    ordering = ['sent_at']  # Default message order

    def perform_create(self, serializer):
        """
        Sets the sender of the message to the authenticated user before saving.
        The conversation is expected to be provided in the request data (conversation_id).
        """
        serializer.save(sender=self.request.user)

    # Optional nested routing logic
    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     conversation_id = self.kwargs.get('conversation_pk')
    #     if conversation_id:
    #         queryset = queryset.filter(conversation__conversation_id=conversation_id)
    #     return queryset
