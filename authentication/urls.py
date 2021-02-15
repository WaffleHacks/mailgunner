from django.urls import path

from . import views

app_name = 'authentication'
urlpatterns = [
    path('login', views.login_view, name='login'),
    path('settings', views.settings, name='settings'),
    path('logout', views.logout_view, name='logout'),
]
