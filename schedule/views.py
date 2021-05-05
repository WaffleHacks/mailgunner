from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import DetailView, ListView
from email.utils import getaddresses
from pathlib import Path

from utils import mail
from .models import Message

DATETIME_FORMAT = "%Y-%m-%d %H:%M"


class BaseIndexView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "schedule/index.html"

    context_object_name = "scheduled"


class QueuedView(BaseIndexView):
    current_tab = "queued"
    description = "are queued to be sent"

    def get_queryset(self):
        return Message.objects.filter(send_at__gte=timezone.now())


class SentView(BaseIndexView):
    current_tab = "sent"
    description = "have been sent"

    def get_queryset(self):
        return Message.objects.order_by("-send_at").filter(send_at__lte=timezone.now())


@login_required
def new(request):
    """
    Schedule a new message to be sent
    """
    if request.method == "GET":
        return render(request, "schedule/send.html", {"new_message": True})

    # Get fields from request
    from_name = request.POST.get("name")
    from_email = request.POST.get("email")
    to = request.POST.get("to")
    subject = request.POST.get("subject")
    send_at = request.POST.get("send_at")
    html = request.POST.get("body")
    plaintext = request.POST.get("plaintext")

    # Ensure all the fields are present
    if not mail.validate_fields(
        request, from_name, from_email, to, subject, html, plaintext
    ):
        return redirect("schedule:new")
    if send_at is None:
        messages.error(request, "Your message must have a date and time to be sent at")

    # Build the mime message to ensure consistency
    mime_message = mail.build_message(
        request, from_name, from_email, to, subject, html, plaintext
    )

    # Parse the date to send it at as a datetime object
    parsed_send_at = datetime.strptime(send_at, DATETIME_FORMAT)

    # Save the scheduled message to the database
    [(parsed_from_name, parsed_from_email)] = getaddresses([mime_message.from_email])
    message = Message(
        from_name=parsed_from_name,
        from_email=parsed_from_email,
        to=to,
        subject=mime_message.subject,
        send_at=parsed_send_at,
        text=plaintext,
        html=html,
    )
    message.save()

    # Extract any attachments
    for attachment in mime_message.attachments:
        # Extract the mime details
        name, content, mime = attachment

        # Get only the filepath
        sanitized_path = Path(name).name

        # Create a tempfile to be uploaded
        temp = TemporaryUploadedFile(name, mime, len(content), "utf-8")
        if type(content) == str:
            temp.write(content.encode())
        else:
            temp.write(content)

        message.attachment_set.create(
            name=sanitized_path, content_type=mime, inline=False, content=temp
        )

    # TODO: queue the message for sending (probably needs celery)

    return redirect("schedule:queued")


class MessageView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = "schedule/message.html"

    context_object_name = "message"


@login_required
def delete(request, pk):
    """
    Delete the specified message
    """
    # Get the message
    message = get_object_or_404(Message, pk=pk)

    # Delete it
    message.delete()

    # Redirect based on whether it was sent or not
    if message.was_sent():
        return redirect("schedule:sent")
    else:
        return redirect("schedule:queued")
