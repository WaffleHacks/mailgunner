from django.urls import path

from . import views

app_name = "external"
urlpatterns = [path("register", views.register, name="register")]
