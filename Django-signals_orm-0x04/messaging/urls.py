from django.urls import path, include, reverse
from . import views

urlpatterns = [
    path('delete-account/', views.delete_user, name='delete_message'),
    path('delete-success/', views.delete_success, name='delete_success'),


]