# messaging_app/chats/urls.py

from django.urls import path, include
from rest_framework_nested import routers
from .views import ConversationViewSet, MessageViewSet # Assuming MessageViewSet is imported

# Create the base router
router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')

# Create a nested router for messages under conversations
convo_router = routers.NestedDefaultRouter(router, r'conversations', lookup='conversation')
convo_router.register(r'messages', MessageViewSet, basename='conversation-messages')


urlpatterns = [
    # Include both the base and nested routes
    path('', include(router.urls)),
    path('', include(convo_router.urls)),

    # --- UNCOMMENT THIS LINE ---
    path('messages/<uuid:pk>/', MessageViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='message-detail'),
    # --- END UNCOMMENT ---
]