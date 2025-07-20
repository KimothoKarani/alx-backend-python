from rest_framework import serializers
from .models import User, Conversation, Message

# Helper Serializer for nested User representation
# This is used when a User object is nested within another serializer (e.g., Message sender, Conversation participants)
# It provides a concise view of the user without exposing sensitive details or excessive information.
class NestedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Fields to include when a User is nested.
        # 'user_id' is crucial for identification.
        fields = ['user_id', 'first_name', 'last_name', 'email']
        # All fields in this nested serializer are read-only, as it's for display purposes.
        read_only_fields = fields

# 1. User Serializer
# This serializer is for the main User API endpoint.
# It defines how User model instances are converted to/from JSON.
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Fields that will be serialized.
        # 'password_hash' is handled internally by Django's 'password' field and is not directly exposed.
        fields = [
            'user_id', 'first_name', 'last_name', 'email', 'phone_number', 'role', 'created_at'
        ]
        # Fields that are automatically generated and should not be modified via API requests.
        read_only_fields = ['user_id', 'created_at']

# 2. Message Serializer
# This serializer defines how Message model instances are converted to/from JSON.
# It handles nested relationships for 'sender' and uses explicit fields for foreign key inputs.
class MessageSerializer(serializers.ModelSerializer):
    # For output (GET requests), represent the 'sender' as a nested object using NestedUserSerializer.
    sender = NestedUserSerializer(read_only=True)

    # For input (POST/PUT requests), allow specifying the sender by their 'user_id'.
    # This field maps directly to the 'sender' ForeignKey on the Message model.
    # It's 'write_only' meaning it's only for input, not included in the response.
    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), # Used for validating the provided user_id
        source='sender',             # Maps this field to the 'sender' attribute on the model
        write_only=True,             # Only visible when writing data (e.g., creating a message)
        help_text='The user_id (UUID) of the sender.'
    )

    # For input, allow specifying the 'conversation' by its 'conversation_id'.
    # Similar to sender_id, this maps to the 'conversation' ForeignKey.
    conversation_id = serializers.PrimaryKeyRelatedField(
        queryset=Conversation.objects.all(), # Used for validating the provided conversation_id
        source='conversation',               # Maps this field to the 'conversation' attribute on the model
        write_only=True,                     # Only visible when writing data
        help_text='The conversation_id (UUID) this message belongs to.'
    )

    class Meta:
        model = Message
        # Include all fields, explicitly separating input-only fields.
        fields = [
            'message_id', 'sender', 'sender_id', 'conversation_id', 'message_body', 'sent_at'
        ]
        # Fields that are automatically generated.
        read_only_fields = ['message_id', 'sent_at']

    # Custom method to represent the object for output.
    # This is to ensure 'conversation' field is represented as its UUID in the output,
    # and not as a complex nested object (unless explicitly requested via another nested serializer).
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Convert the conversation object back to its ID for consistency in output
        # when 'conversation_id' is write_only.
        # This will make the 'conversation_id' field appear in the output with the actual UUID.
        # Note: 'conversation_id' here refers to the field we explicitly created, not the model's FK object.
        # DRF by default would just represent `instance.conversation` as its PK (UUID) if it's in `fields`.
        # However, by setting `conversation_id` as `write_only`, we need to explicitly put it back for output.
        representation['conversation_id'] = str(instance.conversation.conversation_id)
        return representation

# 3. Conversation Serializer
# This serializer defines how Conversation model instances are converted to/from JSON.
# It handles nested lists of 'participants' and 'messages'.
class ConversationSerializer(serializers.ModelSerializer):
    # For output, represent 'participants' as a list of nested User objects.
    # 'many=True' indicates it's a list, and 'read_only=True' for display purposes.
    participants = NestedUserSerializer(many=True, read_only=True)

    # For input (POST/PUT requests), allow specifying 'participants' by a list of 'user_id's.
    # This handles the Many-to-Many relationship for creation/update.
    participant_ids = serializers.PrimaryKeyRelatedField(
        many=True,                        # Expects a list of IDs
        queryset=User.objects.all(),      # Used for validating each user_id in the list
        write_only=True,                  # Only for input
        help_text='List of user_ids (UUIDs) to include as participants in this conversation.'
    )

    # For output, include all messages belonging to this conversation as a list of Message objects.
    # Messages are nested using the MessageSerializer defined above.
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        # Include fields for output ('participants', 'messages') and input ('participant_ids').
        fields = [
            'conversation_id', 'participants', 'participant_ids', 'messages', 'created_at'
        ]
        # Fields that are automatically generated.
        read_only_fields = ['conversation_id', 'created_at']

    # Custom create method to handle the Many-to-Many relationship (participants) on creation.
    def create(self, validated_data):
        # Extract the list of participant IDs from the validated data.
        # This data is popped because it's not a direct field on the Conversation model,
        # but rather handled by the ManyToMany relationship.
        participants_data = validated_data.pop('participant_ids', [])

        # Create the Conversation instance using the remaining validated data.
        conversation = Conversation.objects.create(**validated_data)

        # Add the participants to the newly created conversation.
        # The .set() method handles adding multiple related objects efficiently.
        conversation.participants.set(participants_data)

        return conversation

    # Custom update method to handle the Many-to-Many relationship (participants) on update.
    def update(self, instance, validated_data):
        # Extract participant IDs for update, if provided.
        participants_data = validated_data.pop('participant_ids', None)

        # Update simple fields on the Conversation instance.
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # If new participant IDs were provided, update the Many-to-Many relationship.
        if participants_data is not None:
            instance.participants.set(participants_data)

        # Save the changes to the Conversation instance.
        instance.save()
        return instance