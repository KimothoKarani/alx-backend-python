# Django-Middleware-0x03/chats/middleware.py

import logging  # Import the logging module
from datetime import datetime  # Import datetime for timestamps

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