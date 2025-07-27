# messaging_app/chats/views.py
import django_filters
from rest_framework import viewsets, filters # Import filters
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework import status # Import status for HTTP_403_FORBIDDEN

from .models import User, Conversation, Message
from .serializers import UserSerializer, ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation, IsMessageSenderOrConversationParticipant, IsAuthenticatedCustom # Keep all imports
from .pagination import StandardPagination # <-- Import your custom pagination class
from .filters import MessageFilter # <-- Import your custom filter class

# --- Conversation ViewSet ---
class ConversationViewSet(viewsets.ModelViewSet):
    # ... (existing code for ConversationViewSet) ...
    queryset = Conversation.objects.all().order_by('-updated_at')
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticatedCustom, IsParticipantOfConversation]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['participants__email', 'name']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(participants=self.request.user).distinct()

    def perform_create(self, serializer):
        participant_users = serializer.validated_data.get('participant_ids', [])
        if self.request.user not in participant_users:
            participant_users.append(self.request.user)
        conversation = serializer.save()
        conversation.participants.set(participant_users)


# --- Message ViewSet ---
class MessageViewSet(viewsets.ModelViewSet):
    # ... (existing code for MessageViewSet) ...
    queryset = Message.objects.all().order_by('sent_at')
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticatedCustom, IsMessageSenderOrConversationParticipant]

    # --- Pagination and Filtering Configuration ---
    pagination_class = StandardPagination # <-- Apply custom pagination class
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, django_filters.rest_framework.DjangoFilterBackend] # <-- Add DjangoFilterBackend
    filterset_class = MessageFilter # <-- Apply your custom filter class
    search_fields = ['message_body', 'sender__email'] # Search remains for message_body/sender email
    ordering_fields = ['sent_at']
    ordering = ['sent_at']

    def get_queryset(self):
        conversation_pk = self.kwargs.get('conversation_pk')

        if not conversation_pk:
            # If not a nested route, return base queryset and let filterset_class apply filters if any
            # The permissions (IsMessageSenderOrConversationParticipant.has_object_permission)
            # will handle security for retrieve/update/destroy actions on individual messages
            # accessed directly.
            return super().get_queryset()


        try:
            conversation_messages = Message.objects.filter(
                conversation_id=conversation_pk,
                conversation__participants=self.request.user
            )
            # Make sure it's ordered for consistent pagination and filtering
            return conversation_messages.order_by('sent_at')
        except Exception:
            raise PermissionDenied("Conversation not found or you are not a participant. Status: " + str(status.HTTP_403_FORBIDDEN))


    def perform_create(self, serializer):
        conversation_pk = self.kwargs.get('conversation_pk')
        if not conversation_pk:
            raise ValidationError({"conversation": "Conversation ID must be provided in the URL."})

        try:
            conversation = Conversation.objects.get(
                conversation_id=conversation_pk,
                participants=self.request.user
            )
        except Conversation.DoesNotExist:
            raise PermissionDenied("Conversation not found or you are not a participant. Status: " + str(status.HTTP_403_FORBIDDEN))

        serializer.save(sender=self.request.user, conversation=conversation)