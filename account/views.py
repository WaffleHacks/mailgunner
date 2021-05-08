from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import redirect, render, resolve_url
import requests

from .models import Profile
from .oauth import get_discord_client

MANAGE_SERVER_PERMISSION = 0x20

User = get_user_model()
generator = PasswordResetTokenGenerator()


def login_view(request):
    """
    Display and handle user account
    """
    # Redirect if user already authenticated
    if request.user.is_authenticated:
        return redirect("index")

    # Add the next URL to the session
    if request.GET.get("next"):
        request.session["next"] = request.GET.get("next")

    return render(request, "account/login.html")


def start_login(request):
    """
    Start the OAuth login flow
    """
    client = get_discord_client()

    redirect_url = request.build_absolute_uri(resolve_url("account:oauth_finish"))
    return client.authorize_redirect(request, redirect_url)


def finish_login(request):
    """
    Complete the OAuth login flow
    """
    client = get_discord_client()

    # Handle rejections
    if request.GET.get("error") is not None:
        messages.error(request, "Your login attempt was rejected by Discord")
        return redirect("account:login")

    # Get the access token
    token = client.authorize_access_token(request)
    client.token = token

    # Get the user's info
    user_info = client.userinfo(token=token)

    # Get all the user's guilds
    response = requests.get(
        "https://discord.com/api/v8/users/@me/guilds",
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )
    servers = response.json()

    # Check that the user is allowed to access the server
    # Verifies that the server ids match and that the user
    # is either the owner or has the MANAGE_SEVER permission
    authorized = any(
        map(
            lambda server: server.get("id") == django_settings.DISCORD_GUILD_ID
            and (
                server.get("owner")
                or (
                    int(server.get("permissions")) & MANAGE_SERVER_PERMISSION
                    == MANAGE_SERVER_PERMISSION
                )
            ),
            servers,
        )
    )
    if not authorized:
        messages.error(
            request,
            "Your account does not have the required permissions to access this site!",
        )
        return redirect("account:login")

    # Get the user or register them
    try:
        user = User.objects.filter(
            username=user_info["username"], email=user_info["email"]
        ).get()
    except User.DoesNotExist:
        user = User(username=user_info["username"], email=user_info["email"])
        user.set_unusable_password()
        user.save()
        profile = Profile(user=user, preferred_username=user.username.replace("#", "."))
        profile.save()

    # Login the user
    login(request, user)

    # Remind the user to set their name
    if user.first_name is None or user.last_name is None:
        messages.info(
            request,
            "Welcome to MailGunner! Please set your first and last name on the settings page.",
        )

    # Redirect after successful login
    redirect_to = request.session.pop("next", "index")
    return redirect(redirect_to)


@login_required
def settings(request):
    """
    Enable a user to view/change their preferences
    """
    # Display the form
    if request.method == "GET":
        return render(request, "account/settings.html")

    # Get the user
    user = request.user

    # Change general settings logic
    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")
    preferred_username = request.POST.get("preferred_username")

    # Only modify parameters if non-null and are different than current
    if first_name is not None and first_name != user.first_name:
        user.first_name = first_name
    if last_name is not None and last_name != user.last_name:
        user.last_name = last_name
    if (
        preferred_username is not None
        and preferred_username != user.profile.preferred_username
    ):
        user.profile.preferred_username = preferred_username

    # Save the changes
    user.profile.save()
    user.save()

    return redirect("account:settings")


def logout_view(request):
    """
    Logout a user and redirect them to the login page
    """
    logout(request)
    return redirect("account:login")
