from django.urls import path

from . import views

app_name = "account"
urlpatterns = [
    path("forgot", views.forgot_password, name="forgot"),
    path("reset/<str:uid>/<str:token>", views.reset_password, name="reset"),
    path("login", views.login_view, name="login"),
    path("settings", views.settings, name="settings"),
    path("logout", views.logout_view, name="logout"),
]
