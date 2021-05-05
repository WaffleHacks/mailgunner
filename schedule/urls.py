from django.urls import path

from . import views

app_name = "schedule"
urlpatterns = [
    path("", views.QueuedView.as_view(), name="queued"),
    path("sent", views.SentView.as_view(), name="sent"),
    path("new", views.new, name="new"),
    path("messages/<int:pk>", views.MessageView.as_view(), name="message"),
    path("messages/<int:pk>/delete", views.delete, name="delete"),
]
