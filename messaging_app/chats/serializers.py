from rest_framework import serializers
from .models import User, Conversation, Message

# --- Helper Serializer for Nested User Representation ---
# This serializer provides a concise, read-only view of User details.
# It's used when a User object is included as a nested relationship within other serializers
# (e.g., as a participant in a conversation or a sender of a message).
class NestedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email']
        read_only_fields = fields  # Ensure these fields are read-only when nested


# --- 1. User Serializer ---
# Defines how the User model is serialized/deserialized for main User API endpoints.
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()  # Computed field to show user's full name

    class Meta:
        model = User
        fields = [
            'user_id', 'first_name', 'last_name', 'full_name',
            'email', 'phone_number', 'role', 'created_at'
        ]
        read_only_fields = ['user_id', 'created_at']

    # Combines first and last name for display
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


# --- 2. Message Serializer ---
# Defines how the Message model is serialized/deserialized.
# Handles nested 'sender' relationship for output and uses 'sender_id' for input.
class MessageSerializer(serializers.ModelSerializer):
    sender = NestedUserSerializer(read_only=True)  # Nested output
    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='sender',
        write_only=True,
        help_text='The user_id (UUID) of the sender.'
    )
    conversation_id = serializers.PrimaryKeyRelatedField(
        queryset=Conversation.objects.all(),
        source='conversation',
        write_only=True,
        help_text='The conversation_id (UUID) this message belongs to.'
    )
    message_preview = serializers.CharField(read_only=True, source='message_body')  # Example use of CharField

    class Meta:
        model = Message
        fields = [
            'message_id', 'sender', 'sender_id', 'conversation_id',
            'message_body', 'message_preview', 'sent_at'
        ]
        read_only_fields = ['message_id', 'sent_at', 'message_preview']

    # Include conversation_id in the output even though it's write-only during input
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['conversation_id'] = str(instance.conversation.conversation_id)
        return representation

    # Basic validation: ensure the message body isn't empty or just whitespace
    def validate_message_body(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message body cannot be empty.")
        return value


# --- 3. Conversation Serializer ---
# Defines how the Conversation model is serialized/deserialized.
# Handles nested 'participants' and 'messages' relationships.
class ConversationSerializer(serializers.ModelSerializer):
    participants = NestedUserSerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True,
        help_text='List of user_ids (UUIDs) to include as participants in this conversation.'
    )
    messages = MessageSerializer(many=True, read_only=True)

    # Adds a preview of the latest message, using SerializerMethodField
    latest_message_preview = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'participant_ids',
            'messages', 'latest_message_preview', 'created_at'
        ]
        read_only_fields = ['conversation_id', 'created_at', 'latest_message_preview']

    # Helper to return the latest message body snippet
    def get_latest_message_preview(self, obj):
        latest = obj.messages.order_by('-sent_at').first()
        return latest.message_body[:100] if latest else None

    def create(self, validated_data):
        participants_data = validated_data.pop('participant_ids', [])
        conversation = Conversation.objects.create(**validated_data)
        conversation.participants.set(participants_data)
        return conversation

    def update(self, instance, validated_data):
        participants_data = validated_data.pop('participant_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if participants_data is not None:
            instance.participants.set(participants_data)
        instance.save()
        return instance
