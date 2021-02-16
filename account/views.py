from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.shortcuts import redirect, render

User = get_user_model()
generator = PasswordResetTokenGenerator()


def login_view(request):
    """
    Display and handle user account
    """
    # Display the form
    if request.method == "GET":
        # Redirect if user already authenticated
        if request.user.is_authenticated:
            return redirect("index")
        return render(request, "account/login.html")

    # Get the user reference
    user = authenticate(
        request,
        username=request.POST.get("username"),
        password=request.POST.get("password"),
    )
    if user is None:
        messages.error(request, "Invalid username or password")
        return redirect("account:login")

    # Login the user
    login(request, user)

    # Determine where to redirect the user
    redirect_to = request.POST.get("next")
    if redirect_to is None or redirect_to == "":
        redirect_to = "index"

    return redirect(redirect_to)


def forgot_password(request):
    """
    Begin the password reset flow for a user
    """
    # Display the form
    if request.method == "GET":
        # Redirect if already authenticated
        if request.user.is_authenticated:
            return redirect("index")
        return render(request, "account/forgot.html")

    # Ensure an email is provided
    email = request.POST.get("email")
    if email is None or email == "":
        messages.error(request, "You must provide your email")
        return redirect("account:forgot")

    # Attempt to find a user by email
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Fail silently
        # Give no indication of an account existing
        messages.success(
            request,
            "An password reset mail has been sent if an account exists with that email",
        )
        return redirect("account:forgot")

    # Generate a reset token
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = generator.make_token(user)

    # Generate the reset url
    site = get_current_site(request)
    path = reverse("account:reset", kwargs={"uid": uid, "token": token})
    scheme = "https" if django_settings.HTTPS else "http"
    reset_url = f"{scheme}://{site.domain}{path}"

    # Send the reset email
    user.email_user(
        "Reset your password",
        f"Hi {user.first_name},\n"
        f"Use the following link to reset your password:\n"
        f"{reset_url}\n\n"
        f"If you did not recently attempt to reset your password, "
        f"you can safely ignore this message.",
    )

    messages.success(
        request,
        "You should receive a password reset email shortly, if an account exists with that email",
    )
    return redirect("account:forgot")


def reset_password(request, uid, token):
    """
    Complete the password reset flow
    """
    # Attempt to find the user
    try:
        decoded_uid = urlsafe_base64_decode(uid).decode()
        user = User.objects.get(pk=decoded_uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
        messages.error(request, "This reset link has already been used")
        return redirect("account:login")

    # Validate the reset token
    if not generator.check_token(user, token):
        messages.error(request, "This reset link has already been used")
        return redirect("account:login")

    # Render the template
    if request.method == "GET":
        return render(request, "account/reset.html", {"uid": uid, "token": token})

    # Get passwords from request
    password = request.POST.get("password")
    confirmation = request.POST.get("password-confirm")

    # Ensure passwords present and match
    if password is None or confirmation is None:
        messages.error(request, "Passwords are blank or do not match")
        return redirect("account:reset", uid=uid, token=token)
    elif password != confirmation:
        messages.error(request, "Passwords do not match")
        return redirect("account:reset", uid=uid, token=token)

    # Validate password
    try:
        validate_password(password, user)
    except ValidationError as e:
        for error in e.messages:
            messages.error(
                request,
                error.replace("This password", "Your password").replace(
                    "The password", "Your password"
                ),
            )
        return redirect("account:reset", uid=uid, token=token)

    # Set the password
    user.set_password(password)
    user.save()

    return redirect("account:login")


@login_required
def settings(request):
    """
    Enable a user to view/change their preferences
    """
    # Display the form
    if request.method == "GET":
        return render(request, "account/settings.html")

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
            return redirect("account:settings")
        elif password != confirmation:
            messages.error(request, "Passwords must match")
            return redirect("account:settings")

        # Ensure the password is valid
        try:
            validate_password(password, request.user)
        except ValidationError as e:
            for error in e.messages:
                messages.error(
                    request,
                    error.replace("This password", "Your password").replace(
                        "The password", "Your password"
                    ),
                )
            return redirect("account:settings")

        # Set the new password
        user.set_password(password)
        user.save()

        # Logout the user
        logout(request)

    # Change general settings logic
    elif change_type == "general":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")

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

    return redirect("account:settings")


def logout_view(request):
    """
    Logout a user and redirect them to the login page
    """
    logout(request)
    return redirect("account:login")
