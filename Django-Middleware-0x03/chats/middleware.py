# Django-Middleware-0x03/chats/middleware.py

import logging  # Import the logging module
from datetime import datetime  # Import datetime for timestamps
from django.http import HttpResponseForbidden # Import HttpResponseForbidden
from django.utils import timezone # Import timezone for timezone-aware datetimes

# Get an instance of a logger
# It's good practice to name your logger after its module for clarity
logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """
    Middleware to log each user's request.
    Logs timestamp, user (authenticated or anonymous), and request path.
    """

    def __init__(self, get_response):
        """
        Constructor for the middleware.
        Django calls this once when the web server starts.
        It receives the 'get_response' callable, which represents the next middleware
        or the view itself in the request-response chain.
        """
        self.get_response = get_response
        # You can perform setup tasks here that don't need to be done on every request.
        logger.info("RequestLoggingMiddleware initialized.")

    def __call__(self, request):
        """
        This method is called for every request.
        It's where you implement the logic to process the request and/or response.
        """
        # --- Pre-request processing (before calling the next middleware/view) ---

        # Get the user. If authenticated, it's the User object; otherwise, AnonymousUser.
        # request.user is populated by django.contrib.auth.middleware.AuthenticationMiddleware,
        # which runs *before* our custom middleware if placed correctly in settings.py.
        user = request.user

        # Log the information
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_message)

        # --- Call the next middleware/view in the chain ---
        response = self.get_response(request)

        # --- Post-response processing (after the view has returned a response) ---
        # (For this task, we only need to log on the way in, but this is where you'd add
        #  logic to modify the response or log response details.)

        return response


class RestrictAccessByTimeMiddleware:
    """
    Middleware to restrict access to the messaging app during certain hours.
    Access is allowed ONLY between 6 PM (18:00) and 9 PM (21:00) server time.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.start_hour = 18  # 6 PM
        self.end_hour = 21  # 9 PM (exclusive)
        logger.info(
            f"RestrictAccessByTimeMiddleware initialized. Access allowed between {self.start_hour}:00 and {self.end_hour}:00.")

    def __call__(self, request):
        # We want to restrict access only to the API endpoints for the chat app.
        # This middleware should NOT block access to admin, static files, or token endpoints.
        # Check if the request path starts with '/api/' and is not an authentication endpoint.
        # Adjust this condition based on how broadly you want to apply the restriction.

        # If the request is for API tokens or admin, let it pass (auth/admin access should always be available)
        if request.path.startswith('/api/token/') or \
                request.path.startswith('/admin/') or \
                request.path.startswith('/static/') or \
                request.path.startswith('/api-auth/'):  # For DRF browsable API login/logout
            return self.get_response(request)

        # Assume all other /api/ paths are subject to time restriction
        if request.path.startswith('/api/'):
            now = timezone.now()  # Get current time, timezone-aware
            current_hour = now.hour

            # Logic: Access is denied if current_hour is BEFORE 18 (6 PM) OR current_hour is AT/AFTER 21 (9 PM)
            if current_hour < self.start_hour or current_hour >= self.end_hour:
                logger.warning(
                    f"Access denied to {request.path} at {now.strftime('%H:%M:%S')}. Outside allowed hours ({self.start_hour}:00-{self.end_hour}:00).")
                # Return a 403 Forbidden response
                return HttpResponseForbidden(
                    "Access to chat API is restricted outside of operating hours (6 PM - 9 PM UTC).")

        # If not restricted by time, or if not an API path we care about, pass to next middleware/view
        response = self.get_response(request)
        return response