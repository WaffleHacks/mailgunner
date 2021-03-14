from django.contrib import admin
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin

from .models import Attachment, Category, Message, Thread


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


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin, DynamicArrayMixin):
    list_display = ("name",)
