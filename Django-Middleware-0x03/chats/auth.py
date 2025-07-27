# messaging_app/chats/auth.py

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

# Get the custom User model defined in your chats app
User = get_user_model()

class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using their email address.
    Django's default ModelBackend primarily uses the `USERNAME_FIELD` (which is 'email' in our custom User model).
    This custom backend explicitly clarifies login via email and can be extended for other custom login methods
    (e.g., phone number, or validating against an external system).
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user by their email and password.
        The 'username' argument from the login form/API will be treated as the email.
        """
        try:
            # Look up the user by email (which is our USERNAME_FIELD)
            user = User.objects.get(email=username) # Here, 'username' is actually the email
        except User.DoesNotExist:
            return None # No user found with that email

        # Check the password
        if user.check_password(password):
            return user # Password matches, return the user object
        return None # Password does not match

    def get_user(self, user_id):
        """
        Required by Django's authentication system.
        Retrieves a user instance by their primary key (user_id).
        """
        try:
            # Our User model uses 'user_id' as PK, so we look it up by 'pk'
            # (which automatically maps to the primary_key field of the model)
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None