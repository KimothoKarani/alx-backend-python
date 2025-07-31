from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required # For function-based views
from django.contrib.auth import logout # To log the user out after deletion
from django.contrib import messages # For Django messages feedback
from django.http import HttpResponseForbidden, HttpResponse # For direct responses
from .models import Message

# Assuming you might want to render a confirmation page for deletion.
# If not, you can just process POST and redirect.

@login_required(login_url='login')
def delete_user(request):
    """
    View to allow an authenticated user to delete their own account.
    Expects a POST request for deletion confirmation.
    """
    if request.method == 'POST':
        user = request.user
        user_id = user.id #Get the user's ID before deletion

        #perform the deletion
        user.delete() #This will trigger the post_delete signal on User

        #Log out the user immediately after deletion
        logout(request)

        messages.success(request, f"Your account ({user.email} - ID: {user_id}) has been deleted.")
        return redirect('delete_success')
    return None

def delete_success(request):
    """
    View to display a success message after account deletion.
    """
    return render(request, 'messaging/delete_success.html')

#How to use select_related and prefetch_related in a view -> See models.py to see the Manager class
# messaging/views.py (hypothetical)
def get_messages_with_optimized_data(request):
    # Get top-level messages (those without a parent) and prefetch their replies
    messages = Message.objects.with_related_data().filter(parent_message__isnull=True)
    # Now, when you access message.sender, message.receiver, message.parent_message, or message.replies.all()
    # for any 'message' in 'messages', the data is already pre-fetched.
    return render(request, 'messages.html', {'messages': messages})

