from django.urls import path, include, reverse
from . import views

urlpatterns = [
    path('delete-account/', views.delete_user, name='delete_message'),
    path('delete-success/', views.delete_success, name='delete_success'),

    # New paths for messaging features
    path('send-message/', views.create_message, name='send_message'),  # For the message creation form
    path('messages/', views.message_list, name='message_list'),  # For listing messages


]