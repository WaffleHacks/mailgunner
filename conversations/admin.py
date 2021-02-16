from django.contrib import admin

from .models import Attachment, Message, Thread


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("name", "content_type", "inline", "message")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender_email", "recipient_email", "timestamp", "subject")


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = (
        "originally_from",
        "recipient",
        "subject",
        "last_updated",
        "assignee",
    )
