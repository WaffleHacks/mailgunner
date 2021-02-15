from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView
import magic
from pathlib import Path

from .models import Thread


class BaseThreadView(LoginRequiredMixin, ListView):
    model = Thread

    paginate_by = 25
    context_object_name = 'threads'


class UnclaimedView(BaseThreadView):
    template_name = 'conversations/index_unclaimed.html'

    def get_queryset(self):
        return self.model.objects.filter(assignee=None)


class ClaimedView(BaseThreadView):
    template_name = 'conversations/index_claimed.html'

    def get_queryset(self):
        return self.model.objects.filter(assignee=self.request.user)


class ThreadView(LoginRequiredMixin, DetailView):
    model = Thread
    template_name = 'conversations/thread.html'

    context_object_name = 'thread'

    def get_object(self, queryset=None):
        # Get the thread
        thread = super(ThreadView, self).get_object(queryset=queryset)

        # Prevent users that didn't claim a thread from viewing it
        if thread.assignee != self.request.user and thread.assignee is not None:
            messages.error(self.request, "This thread has been claimed by someone else!")
            return redirect('conversations:unclaimed')

        # Mark it as read
        thread.unread = False
        thread.save()

        return thread


@login_required
def claim(request, pk):
    """
    Assign a thread to the requester
    """
    thread = get_object_or_404(Thread, pk=pk)

    # Check that it is not already assigned
    if thread.assignee is not None:
        messages.error(
            request,
            f"This thread is already claimed by {'you' if thread.assignee == request.user else 'someone'}"
        )
        return redirect('conversations:thread', pk=pk)

    # Assign to the user
    thread.assignee = request.user
    thread.save()

    messages.success(request, "Successfully claimed this thread!")
    return redirect('conversations:thread', pk=pk)


@login_required
def unclaim(request, pk):
    """
    Remove a thread from the requester
    """
    thread = get_object_or_404(Thread, pk=pk)

    # Check that it is assigned
    if thread.assignee is None:
        messages.error(request, "This thread is already unclaimed!")
        return redirect('conversations:thread', pk=pk)

    # Check that it is assigned to the requester
    if thread.assignee != request.user:
        messages.error(request, "You cannot unclaim someone else's thread!")
        return redirect('conversations:thread', pk=pk)

    # Remove from the user
    thread.assignee = None
    thread.save()

    messages.success(request, "Successfully unclaimed this thread!")
    return redirect('conversations:thread', pk=pk)


@login_required
def reply(request, pk):
    """
    Reply to a thread
    """
    # Get the thread
    thread = get_object_or_404(Thread, pk=pk)

    # Check that it is assigned to the requester
    if thread.assignee != request.user and thread.assignee is not None:
        messages.error(request, "You cannot reply to someone else's thread!")
        return redirect('conversations:thread', pk=pk)

    # Get the last message that was sent that wasn't from an @wafflehacks.tech email
    previous_messages = thread.message_set.all()
    last_message = previous_messages[0]
    for last_message in previous_messages:
        if "wafflehacks.tech" not in last_message.from_email:
            break

    # Render the template on initial request
    if request.method == "GET":
        return render(request, 'conversations/reply.html', {
            'thread': thread,
            'last_message': last_message,
            'new_message': False
        })

    # Get fields from request
    from_name = request.POST.get('name')
    from_email = request.POST.get('email')
    subject = request.POST.get('subject')
    body = request.POST.get('body')

    # Get all the previous message ids for the References header
    message_ids = '\n'.join([msg.message_id for msg in previous_messages.reverse()])

    # Queue the message for sending
    is_successful = dispatch_message(request, from_name, from_email,
                                     f"{last_message.from_name} <{last_message.from_email}>", subject, body,
                                     last_message.message_id, message_ids)
    if not is_successful:
        return redirect('conversations:reply', pk=thread.pk)

    messages.success(request, "Successfully queued your reply for sending! "
                              "It will be added below once it is successfully sent.")
    return redirect('conversations:thread', pk=pk)


@login_required
def delete(request, pk):
    """
    Delete the specified message
    """
    # Get the thread
    thread = get_object_or_404(Thread, pk=pk)

    # Check that it is assigned to the requester
    if thread.assignee != request.user and thread.assignee is not None:
        messages.error(request, "You cannot delete someone else's thread!")
        return redirect('conversations:thread', pk=pk)

    # Delete the thread
    thread.delete()

    return redirect('conversations:unclaimed')


@login_required
def send(request):
    """
    Send a new message (starts a new thread)
    """
    if request.method == "GET":
        return render(request, "conversations/send.html", {"new_message": True})

    # Get fields from request
    from_name = request.POST.get('name')
    from_email = request.POST.get('email')
    to = request.POST.get('to')
    subject = request.POST.get('subject')
    body = request.POST.get('body')

    # Queue the message for sending
    is_successful = dispatch_message(request, from_name, from_email, to, subject, body)
    if not is_successful:
        return redirect('conversations:send')

    messages.success(request, "Successfully queued your message for sending! "
                              "It will be added below once it is successfully sent.")
    return redirect('conversations:unclaimed')


def dispatch_message(request, from_name: str, from_email: str, to: str, subject: str, body: str,
                     in_reply_to: str = None, references: str = None):
    """
    Dispatch a message through MailGun

    :param request: the Django request
    :param from_name: who the mail is from
    :param from_email: the address the mail is from
    :param to: who the mail is to
    :param subject: the subject of the message
    :param body: the content of the message
    :param in_reply_to: what message the email is replying to
    :param references: other messages in the thread
    :return: whether the queuing was successful
    """
    # Ensure that all fields are present
    if from_name is None:
        messages.error(request, "The from name cannot be blank")
        return False
    if from_email is None:
        messages.error(request, "The from email cannot be blank")
        return False
    if to is None:
        messages.error(request, "The to email cannot be blank")
        return False
    if subject is None:
        messages.error(request, "There must be a subject for your reply")
        return False
    if body is None:
        messages.error(request, "Your reply must have some content")
        return False

    # Ensure the from email is valid
    if "@" in from_email:
        messages.error(request, f"Invalid username for the from email! Got {from_email}@wafflehacks.tech")
        return False

    # Build the message
    message = EmailMessage(
        subject=subject,
        body=body,
        to=[to],
        from_email=f"{from_name} <{from_email}@wafflehacks.tech>",
    )

    # Add reply headers
    if in_reply_to is not None and references is not None:
        message.extra_headers['In-Reply-To'] = in_reply_to
        # TODO: fix references header (waiting on MailGun support)
        message.extra_headers['References'] = references

    # Get and add attachments
    for file in request.FILES.values():
        # Determine the MIME type of the uploaded file and read the content
        if isinstance(file, TemporaryUploadedFile):
            mime = magic.from_file(file.temporary_file_path(), mime=True)
            path = Path(file.temporary_file_path())
            with path.open('rb') as f:
                content = f.read()
        else:
            content = file.read()
            mime = magic.from_buffer(content, mime=True)

        # Attach the file to the message
        message.attach(file.name, content, mime)

    # Queue the message for sending
    message.send()

    return True
