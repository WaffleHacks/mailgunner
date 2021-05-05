from django.contrib import admin

from .models import ScheduledAttachment, ScheduledMessage


@admin.register(ScheduledAttachment)
class ScheduledAttachmentAdmin(admin.ModelAdmin):
    list_display = ("name", "content_type", "inline", "message")


@admin.register(ScheduledMessage)
class ScheduledMessageAdmin(admin.ModelAdmin):
    list_display = ("from_name", "from_email", "to", "subject", "send_at")
