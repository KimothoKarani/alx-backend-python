# messaging_app/chats/urls.py

from django.urls import path, include
from rest_framework_nested import routers  #Import NestedDefaultRouter
from .views import ConversationViewSet, MessageViewSet

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
]
