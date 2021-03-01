from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

User = get_user_model()


@csrf_exempt
def register(request):
    """
    Allow a user to register themselves
    """
    # Ensure they can register
    if request.GET.get("token") != settings.REGISTRATION_TOKEN:
        return error("invalid registration token")

    # Get all the request data
    first_name = request.POST.get("first-name")
    last_name = request.POST.get("last-name")
    email = request.POST.get("email")
    username = request.POST.get("username")
    password = request.POST.get("password")

    # Ensure everything is present
    if first_name is None or last_name is None or username is None or email is None or password is None:
        return error("missing at least one of: 'first-name', 'last-name', 'username', 'email', and 'password'")

    # Check that the username is not already taken
    if len(User.objects.filter(username=username)) != 0:
        return error("username already in use")
    elif len(User.objects.filter(email=email)) != 0:
        return error("email already in use")

    # Create the base user
    user = User(username=username, first_name=first_name, last_name=last_name, email=email)

    # Validate the email and password
    try:
        validate_email(email)
    except ValidationError:
        return error("invalid email address")
    try:
        validate_password(password)
    except ValidationError as e:
        messages = map(
            lambda m: m.replace("This password", "your password")
            .replace("The password", "your password")
            .replace(".", ""),
            e.messages,
        )
        return error(f"invalid password: {'; '.join(messages)}")

    # Set the user's password
    user.set_password(password)
    user.save()

    return JsonResponse({"success": True})


def error(message):
    """
    Generate an error response
    :param message: the reason why it failed
    :return: a standardized JSON error message
    """
    return JsonResponse({"success": False, "reason": message})
