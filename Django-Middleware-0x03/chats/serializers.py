# messaging_app/chats/serializers.py

from rest_framework import serializers
from .models import User, Conversation, Message


# --- Helper Serializer for Nested User Representation ---
class NestedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email']
        read_only_fields = fields


# --- 1. User Serializer ---
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'user_id', 'first_name', 'last_name', 'full_name',
            'email', 'phone_number', 'role', 'created_at'
        ]
        read_only_fields = ['user_id', 'created_at']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


# --- 2. Message Serializer ---
class MessageSerializer(serializers.ModelSerializer):
    sender = NestedUserSerializer(read_only=True)

    # The PrimaryKeyRelatedField for sender and conversation is write-only,
    # meaning they are used for input, but the actual object `sender` and `conversation`
    # fields are used for output. No explicit `sender_id` or `conversation_id` needed here in `fields`.
    # These fields correctly map the incoming IDs to the model instances.
    # The actual sender and conversation instances will be set in the view's perform_create.

    class Meta:
        model = Message
        # Remove sender_id and conversation_id from fields, as they are write_only
        # 'sender' and 'conversation' (the FK instances) are read_only and automatically handled
        fields = [
            'message_id', 'sender', 'conversation',  # 'conversation' will show Conversation ID by default
            'message_body', 'sent_at'
        ]
        read_only_fields = ['message_id', 'sent_at', 'sender',
                            'conversation']  # conversation is read-only when used as an output field

    # Basic validation: ensure the message body isn't empty or just whitespace
    def validate_message_body(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message body cannot be empty.")
        return value

    # Optional: If you want to explicitly show 'sender_id' and 'conversation_id' in output besides the nested objects
    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     representation['sender_id'] = str(instance.sender.user_id)
    #     representation['conversation_id'] = str(instance.conversation.conversation_id)
    #     return representation


# --- 3. Conversation Serializer ---
class ConversationSerializer(serializers.ModelSerializer):
    participants = NestedUserSerializer(many=True, read_only=True)
    # participant_ids is for INPUT only (for creating/updating participants)
    participant_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),  # Needs to be able to find all users
        write_only=True,
        help_text='List of user_ids (UUIDs) to include as participants in this conversation.'
    )
    messages = MessageSerializer(many=True, read_only=True)  # Nested messages will be displayed

    latest_message_preview = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'name', 'participants', 'participant_ids',
            'messages', 'latest_message_preview', 'created_at', 'updated_at'  # Add 'name' and 'updated_at' here
        ]
        read_only_fields = ['conversation_id', 'participants', 'messages', 'latest_message_preview', 'created_at',
                            'updated_at']
        # 'name' is not read_only if you want to allow setting/updating it

    def get_latest_message_preview(self, obj):
        latest = obj.messages.order_by('-sent_at').first()
        return latest.message_body[:100] if latest else None

    # Overriding create and update to handle the many-to-many relationship for participants
    def create(self, validated_data):
        # participants_data is a list of User instances thanks to PrimaryKeyRelatedField
        participants_data = validated_data.pop('participant_ids', [])

        # Create conversation without participants first
        conversation = Conversation.objects.create(**validated_data)

        # Add participants to the conversation after it's created
        conversation.participants.set(participants_data)
        return conversation

    def update(self, instance, validated_data):
        # participants_data will be None if 'participant_ids' was not provided in the request
        participants_data = validated_data.pop('participant_ids', None)

        # Update other fields first
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Only update participants if 'participant_ids' was actually provided in the request
        if participants_data is not None:
            instance.participants.set(participants_data)

        instance.save()
        return instance