# chats/management/commands/seed_db.py
from django.core.management.base import BaseCommand
from chats.models import User, Conversation, Message
from django.utils import timezone

class Command(BaseCommand):
    help = "Seed the database with sample data"

    def handle(self, *args, **kwargs):
        alice = User.objects.create_user(
            email="alice@example.com",
            password="password123",
            first_name="Alice",
            last_name="Wonderland",
            role="admin"
        )
        bob = User.objects.create_user(
            email="bob@example.com",
            password="password123",
            first_name="Bob",
            last_name="Builder",
            role="guest"
        )

        convo = Conversation.objects.create(name="Test Chat")
        convo.participants.set([alice, bob])

        Message.objects.create(
            sender=alice,
            conversation=convo,
            message_body="Hi Bob!",
            sent_at=timezone.now()
        )
        Message.objects.create(
            sender=bob,
            conversation=convo,
            message_body="Hey Alice!",
            sent_at=timezone.now()
        )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully."))
