from django.urls import path

from . import views

app_name = "account"
urlpatterns = [
    path("login", views.login_view, name="login"),
    path("oauth/start", views.start_login, name="oauth_start"),
    path("oauth/authorize", views.finish_login, name="oauth_finish"),
    path("settings", views.settings, name="settings"),
    path("logout", views.logout_view, name="logout"),
]
