from django.urls import path

from . import views

app_name = "conversations"
urlpatterns = [
    path("unclaimed", views.UnclaimedView.as_view(), name="unclaimed"),
    path("claimed", views.ClaimedView.as_view(), name="claimed"),
    path("send", views.send, name="send"),
    path("threads/<int:pk>", views.ThreadView.as_view(), name="thread"),
    path("threads/<int:pk>/reply", views.reply, name="reply"),
    path("threads/<int:pk>/assign", views.claim, name="claim"),
    path("threads/<int:pk>/unassign", views.unclaim, name="unclaim"),
    path("threads/<int:pk>/delete", views.delete, name="delete"),
]
