from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render


def login_view(request):
    """
    Display and handle user authentication
    """
    # Display the form
    if request.method == "GET":
        # Redirect if user already authenticated
        if request.user.is_authenticated:
            return redirect('')
        return render(request, 'authentication/login.html')

    # Get the user reference
    user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
    if user is None:
        return render(request, 'authentication/login.html', {'error': 'Invalid username or password'})

    # Login the user
    login(request, user)

    return redirect('')


def logout_view(request):
    """
    Logout a user and redirect them to the login page
    """
    logout(request)
    return redirect('authentication:login')
