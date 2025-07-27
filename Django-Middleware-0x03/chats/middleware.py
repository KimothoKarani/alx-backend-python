# Django-Middleware-0x03/chats/middleware.py

import logging  # Import the logging module
from datetime import datetime, timedelta  # Import datetime for timestamps
from zoneinfo import ZoneInfo

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
        self.start_hour = 16  # 6 PM
        self.end_hour = 22  # 9 PM (exclusive)
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
            now = timezone.now().astimezone(ZoneInfo('Africa/Nairobi'))
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


# --- NEW MIDDLEWARE: OffensiveLanguageMiddleware (Rate Limiting) ---
class OffensiveLanguageMiddleware:  # Renamed as per task, but implements rate limiting
    """
    Middleware to limit the number of chat messages (POST requests to message endpoints)
    a user can send within a certain time window, based on their IP address.
    """
    # Stores IP addresses and their request timestamps:
    # { 'ip_address': [timestamp1, timestamp2, ...], ... }
    _requests_per_ip = {}

    # Configuration for rate limiting
    MESSAGE_LIMIT = 5
    TIME_WINDOW_SECONDS = 60  # 1 minute

    def __init__(self, get_response):
        self.get_response = get_response
        logger.info(
            f"OffensiveLanguageMiddleware (Rate Limiter) initialized. Limit: {self.MESSAGE_LIMIT} messages per {self.TIME_WINDOW_SECONDS} seconds.")

    def __call__(self, request):
        # We only care about POST requests to message creation endpoints
        # This regex covers /api/conversations/{conv_pk}/messages/
        # or direct /api/messages/ (if you added a POST method to that route)
        is_message_post = request.method == 'POST' and \
                          (request.path.startswith(
                              '/api/conversations/') and '/messages/' in request.path)  # Or add direct '/api/messages/'

        if is_message_post:
            ip_address = self._get_client_ip(request)
            now = timezone.now()

            # Clean up old timestamps for this IP
            # Filter out timestamps older than the time window
            if ip_address in self._requests_per_ip:
                self._requests_per_ip[ip_address] = [
                    t for t in self._requests_per_ip[ip_address]
                    if now - t < timedelta(seconds=self.TIME_WINDOW_SECONDS)
                ]
            else:
                self._requests_per_ip[ip_address] = []

            # Check if adding the current request exceeds the limit
            if len(self._requests_per_ip[ip_address]) >= self.MESSAGE_LIMIT:
                logger.warning(f"Rate limit exceeded for IP: {ip_address}. Path: {request.path}")
                # Return a 429 Too Many Requests response (standard for rate limiting)
                # Or 403 Forbidden as requested in the task. Let's use 403 as per instruction.
                return HttpResponseForbidden(
                    f"Too many messages from your IP. Please try again after {self.TIME_WINDOW_SECONDS} seconds.")

            # If not exceeded, add current timestamp
            self._requests_per_ip[ip_address].append(now)
            logger.info(
                f"IP {ip_address} sent message. Count: {len(self._requests_per_ip[ip_address])} in {self.TIME_WINDOW_SECONDS}s.")

        response = self.get_response(request)
        return response

    def _get_client_ip(self, request):
        """
        Helper function to get the client's IP address.
        Considers X-Forwarded-For header for proxies.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# --- NEW MIDDLEWARE: RolePermissionMiddleware ---
class RolepermissionMiddleware:
    """
    Middleware to restrict access to specific API actions based on the user's role.
    Only 'admin' users are allowed to access the specified paths.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Define paths that require 'admin' role
        # Example: if only admins can access '/api/admin/users/' or specific Conversation management
        self.restricted_paths_for_admin = [
            '/api/admin/',  # If you had an admin-specific API endpoint
            # '/api/conversations/', # Uncomment if only admins can list ALL conversations (GET) or create/delete ANY conversation (POST/DELETE)
            # '/api/messages/', # Uncomment if only admins can list ALL messages
        ]
        # Or you could specify methods for paths:
        # self.restricted_actions_by_role = {
        #     'admin': {
        #         ('DELETE', '/api/conversations/'): True, # Only admin can DELETE any conversation
        #         ('PUT', '/api/users/'): True, # Only admin can PUT/PATCH users
        #     }
        # }
        logger.info("RolePermissionMiddleware initialized.")

    def __call__(self, request):
        # Allow non-API paths, static files, and authentication endpoints to pass always.
        if not request.path.startswith('/api/') or \
                request.path.startswith('/api/token/') or \
                request.path.startswith('/admin/') or \
                request.path.startswith('/static/') or \
                request.path.startswith('/api-auth/'):
            return self.get_response(request)

        # Check if user is authenticated (crucial, as 'request.user' might be AnonymousUser otherwise)
        # This middleware should run AFTER AuthenticationMiddleware
        if not request.user.is_authenticated:
            # If the path is protected for specific roles, but user is not authenticated,
            # this middleware returns 403. DRF's IsAuthenticated would also catch this,
            # but this middleware enforces it earlier for role-specific paths.
            # However, for role checks, we need them to be AUTHENTICATED.
            # If default permission is IsAuthenticated, this check is redundant but safe.
            # For this task, we want to check role if it's a restricted path.
            # If user is not authenticated AND path is restricted, deny.

            # Simple check: If user hits any defined restricted path and isn't admin
            for path_prefix in self.restricted_paths_for_admin:
                if request.path.startswith(path_prefix):
                    if request.user.is_authenticated and request.user.role == 'admin':
                        return self.get_response(request)  # Admin user allowed
                    else:
                        logger.warning(
                            f"Access denied: User {request.user} (Role: {getattr(request.user, 'role', 'N/A')}) tried to access restricted path {request.path}.")
                        return HttpResponseForbidden(
                            "Access Denied: You do not have the required role to access this resource.")

            # If the path is not explicitly restricted for admins OR if user is authenticated and not admin
            # let it pass to DRF's permissions. DRF permissions are more granular.
            # This middleware is for broad, early role-based blocks.

            # For task: if user is NOT admin/moderator, return 403 for specific actions.
            # Let's say we want to restrict all DELETE requests or all POST to conversations
            # unless the user is an admin.

            # Example: Restrict all DELETE requests to /api/conversations/ to admins only
            # This is a strong, broad restriction.
            if request.method == 'DELETE' and request.path.startswith('/api/conversations/'):
                if not request.user.is_authenticated or request.user.role != 'admin':
                    logger.warning(
                        f"Access denied: Non-admin user {request.user} tried to DELETE conversation at {request.path}.")
                    return HttpResponseForbidden("Access Denied: Only administrators can delete conversations.")

            # Example: Restrict all POST requests to /api/conversations/ (conversation creation) to admins only
            # if request.method == 'POST' and request.path == '/api/conversations/':
            #     if not request.user.is_authenticated or request.user.role != 'admin':
            #         logger.warning(f"Access denied: Non-admin user {request.user} tried to create conversation at {request.path}.")
            #         return HttpResponseForbidden("Access Denied: Only administrators can create conversations.")

        # If no explicit role-based restriction is triggered by this middleware,
        # pass the request to the next in chain (which will be DRF's permissions).
        response = self.get_response(request)
        return response