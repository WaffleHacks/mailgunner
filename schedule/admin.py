from django.contrib import admin

from .models import Attachment, Message


@admin.register(Attachment)
class ScheduledAttachmentAdmin(admin.ModelAdmin):
    list_display = ("name", "content_type", "inline", "message")


@admin.register(Message)
class ScheduledMessageAdmin(admin.ModelAdmin):
    list_display = ("from_name", "from_email", "to", "subject", "send_at")
