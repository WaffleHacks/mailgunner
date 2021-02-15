from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import redirect, render


def login_view(request):
    """
    Display and handle user authentication
    """
    # Display the form
    if request.method == "GET":
        # Redirect if user already authenticated
        if request.user.is_authenticated:
            return redirect('index')
        return render(request, 'authentication/login.html')

    # Get the user reference
    user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
    if user is None:
        return render(request, 'authentication/login.html', {'error': 'Invalid username or password'})

    # Login the user
    login(request, user)

    return redirect('index')


@login_required
def settings(request):
    """
    Enable a user to view/change their preferences
    """
    # Display the form
    if request.method == "GET":
        return render(request, 'authentication/settings.html')

    # Determine the type of modification
    change_type = request.POST.get("type")

    # Get the user
    user = request.user

    # Change password logic
    if change_type == "password":
        password = request.POST.get("password")
        confirmation = request.POST.get("password-confirm")

        # Validate passwords
        if password is None or confirmation is None:
            messages.error(request, "Passwords are blank or do not match")
            return redirect('authentication:settings')
        elif password != confirmation:
            messages.error(request, "Passwords must match")
            return redirect('authentication:settings')

        # Ensure the password is valid
        try:
            validate_password(password, request.user)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error
                               .replace('This password', 'Your password')
                               .replace('The password', 'Your password'))
            return redirect('authentication:settings')

        # Set the new password
        user.set_password(password)
        user.save()

        # Logout the user
        logout(request)

    # Change general settings logic
    elif change_type == "general":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')

        # Only modify parameters if non-null and are different than current
        if first_name is not None and first_name != request.user.first_name:
            user.first_name = first_name
        if last_name is not None and last_name != user.last_name:
            user.last_name = last_name
        if username is not None and username != user.username:
            user.username = username
        if email is not None and email != user.email:
            user.email = email

        # Attempt to save the changes
        try:
            user.save()
        except IntegrityError:
            messages.error(request, "That username is already in use")

    return redirect('authentication:settings')


def logout_view(request):
    """
    Logout a user and redirect them to the login page
    """
    logout(request)
    return redirect('authentication:login')
