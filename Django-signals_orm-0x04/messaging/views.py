from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required # For function-based views
from django.contrib.auth import logout # To log the user out after deletion
from django.contrib import messages # For Django messages feedback
from django.http import HttpResponseForbidden, HttpResponse # For direct responses

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

