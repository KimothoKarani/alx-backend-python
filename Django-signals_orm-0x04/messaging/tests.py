from django.test import TestCase
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from messaging.models import User, Message, Notification


class UserModelTests(TestCase):

    def test_create_user_with_email_and_name(self):
        """Test creating a user with valid email and names."""
        user = User.objects.create_user(
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
            password="password123"
        )
        self.assertEqual(user.email, "testuser@example.com")
        self.assertEqual(user.get_full_name(), "Test User")
        self.assertTrue(user.check_password("password123"))

    def test_email_is_required(self):
        """Test that creating a user without email raises an error."""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email="",
                first_name="No",
                last_name="Email",
                password="password123"
            )

    def test_unique_email_constraint(self):
        """Test that two users cannot have the same email."""
        User.objects.create_user(
            email="unique@example.com",
            first_name="First",
            last_name="User",
            password="password123"
        )
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email="unique@example.com",
                first_name="Duplicate",
                last_name="User",
                password="password123"
            )


class MessageModelTests(TestCase):

    def setUp(self):
        self.sender = User.objects.create_user(
            email="sender@example.com",
            first_name="Sender",
            last_name="User",
            password="password123"
        )
        self.receiver = User.objects.create_user(
            email="receiver@example.com",
            first_name="Receiver",
            last_name="User",
            password="password123"
        )

    def test_message_creation(self):
        """Test creating a message between two users."""
        msg = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello, this is a test message."
        )
        self.assertEqual(msg.sender, self.sender)
        self.assertEqual(msg.receiver, self.receiver)
        self.assertFalse(msg.is_read)
        self.assertIn("Hello", msg.content)

    def test_message_string_representation(self):
        """Test string representation of a message."""
        msg = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message string."
        )
        self.assertIn("Message from", str(msg))


class NotificationModelTests(TestCase):

    def setUp(self):
        self.sender = User.objects.create_user(
            email="sender@example.com",
            first_name="Sender",
            last_name="User",
            password="password123"
        )
        self.receiver = User.objects.create_user(
            email="receiver@example.com",
            first_name="Receiver",
            last_name="User",
            password="password123"
        )
        self.message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="This is a message for notification testing."
        )

    def test_notification_creation(self):
        """Test creating a notification linked to a message."""
        notification = Notification.objects.create(
            message=self.message,
            user=self.receiver,
            content="You have a new message."
        )
        self.assertEqual(notification.user, self.receiver)
        self.assertFalse(notification.is_read)
        self.assertIn("new message", notification.content)

    def test_notification_unique_constraint(self):
        """Test that a user cannot have duplicate notifications for the same message."""
        Notification.objects.create(
            message=self.message,
            user=self.receiver,
            content="You have a new message."
        )
        with self.assertRaises(IntegrityError):
            Notification.objects.create(
                message=self.message,
                user=self.receiver,
                content="Duplicate notification."
            )

    def test_notification_string_representation(self):
        """Test string representation of a notification."""
        # ✅ Use a different message to avoid unique constraint error
        new_message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Another message for testing representation."
        )
        notification = Notification.objects.create(
            message=new_message,
            user=self.receiver,
            content="Notification text here."
        )
        self.assertIn("Notification for", str(notification))
