# messaging_app/chats/filters.py

import django_filters
from django.db.models import Q # For complex OR queries
from .models import Message, User # Import Message and User models

class MessageFilter(django_filters.FilterSet):
    """
    Filter for Message objects.
    - `sender_email`: Filter by sender's email address (case-insensitive contains).
    - `start_date`: Messages sent after or on this date (e.g., YYYY-MM-DD).
    - `end_date`: Messages sent before or on this date (e.g., YYYY-MM-DD).
    - `participant_email`: Filter messages from conversations involving a specific participant email.
    """
    # Filter by sender's email (case-insensitive partial match)
    sender_email = django_filters.CharFilter(
        field_name='sender__email',
        lookup_expr='icontains',
        help_text="Filter messages by sender's email (case-insensitive partial match)."
    )

    # Filter messages sent after or on a specific date
    start_date = django_filters.DateFilter(
        field_name='sent_at',
        lookup_expr='gte',
        help_text="Filter messages sent on or after this date (YYYY-MM-DD)."
    )

    # Filter messages sent before or on a specific date
    end_date = django_filters.DateFilter(
        field_name='sent_at',
        lookup_expr='lte',
        help_text="Filter messages sent on or before this date (YYYY-MM-DD)."
    )

    # Filter messages from conversations involving a specific participant email
    # This requires looking through the ManyToMany relationship
    participant_email = django_filters.CharFilter(method='filter_by_participant_email',
                                                  help_text="Filter messages in conversations involving a participant's email (case-insensitive partial match).")

    def filter_by_participant_email(self, queryset, name, value):
        # Filter conversations that have a participant matching the email
        # Then retrieve all messages within those conversations
        return queryset.filter(conversation__participants__email__icontains=value).distinct()

    class Meta:
        model = Message
        fields = {
            'sender': ['exact'], # Filter by exact sender user_id UUID
            'conversation': ['exact'], # Filter by exact conversation_id UUID
            'message_body': ['icontains'], # Filter message body (case-insensitive contains)
        }
        # Explicitly list fields for filterset, or use '__all__'
        # fields = ['sender', 'conversation', 'message_body', 'sent_at'] # Can list here too