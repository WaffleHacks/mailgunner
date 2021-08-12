from django.urls import path

from . import views

app_name = "conversations"
urlpatterns = [
    path("", views.index, name="index"),
    path("send", views.send, name="send"),
    path("<str:name>", views.index, name="category"),
    path("threads/<int:pk>", views.ThreadView.as_view(), name="thread"),
    path("threads/<int:pk>/reply", views.reply, name="reply"),
    path("threads/<int:pk>/assign", views.claim, name="claim"),
    path("threads/<int:pk>/unassign", views.unclaim, name="unclaim"),
    path("threads/<int:pk>/toggle", views.toggle_unread, name="toggle_unread"),
    path(
        "threads/<int:pk>/change-category",
        views.change_category,
        name="change_category",
    ),
    path("threads/<int:pk>/delete", views.delete, name="delete"),
]
