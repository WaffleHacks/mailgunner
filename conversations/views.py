from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView

from utils import mail
from .models import Category, Thread

# Format for the HTML email
HTML_EMAIL_FORMAT = (
    '<!doctype html><head><meta name="viewport" content="width=device-width"/>'
    '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>'
    "<title>{subject}</title></head><body>{html}</body></html>"
)


@login_required
def index(request, name: str = None):
    """
    Display the threads for a given category
    """
    # Get the names of all the categories
    categories = Category.objects.values("name").all()
    categories = ["Uncategorized"] + list(map(lambda c: c["name"], categories))

    # Get the category and the threads in it
    if name:
        name = name.title()
        category = Category.objects.filter(name=name).get()
        threads = category.thread_set.filter(
            Q(assignee=request.user) | Q(assignee=None)
        ).all()
    else:
        category = Category(name="Uncategorized", addresses=[])
        threads = Thread.objects.filter(
            Q(assignee=request.user) | Q(assignee=None), category=None
        ).all()

    return render(
        request,
        "conversations/index.html",
        {"threads": threads, "category": category, "categories": categories},
    )


class ThreadView(LoginRequiredMixin, DetailView):
    model = Thread
    template_name = "conversations/thread.html"

    context_object_name = "thread"

    def get_object(self, queryset=None):
        # Get the thread
        thread = super(ThreadView, self).get_object(queryset=queryset)

        # Prevent users that didn't claim a thread from viewing it
        if thread.assignee != self.request.user and thread.assignee is not None:
            messages.error(
                self.request, "This thread has been claimed by someone else!"
            )
            return redirect("conversations:index")

        # Mark it as read
        thread.unread = False
        thread.save()

        return thread

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context


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
            f"This thread is already claimed by {'you' if thread.assignee == request.user else 'someone'}",
        )
        return redirect("conversations:thread", pk=pk)

    # Assign to the user
    thread.assignee = request.user
    thread.save()

    messages.success(request, "Successfully claimed this thread!")
    return redirect("conversations:thread", pk=pk)


@login_required
def unclaim(request, pk):
    """
    Remove a thread from the requester
    """
    thread = get_object_or_404(Thread, pk=pk)

    # Check that it is assigned
    if thread.assignee is None:
        messages.error(request, "This thread is already unclaimed!")
        return redirect("conversations:thread", pk=pk)

    # Check that it is assigned to the requester
    if thread.assignee != request.user:
        messages.error(request, "You cannot unclaim someone else's thread!")
        return redirect("conversations:thread", pk=pk)

    # Remove from the user
    thread.assignee = None
    thread.save()

    messages.success(request, "Successfully unclaimed this thread!")
    return redirect("conversations:thread", pk=pk)


@login_required
def change_category(request, pk):
    """
    Change the category of a thread
    """
    # Get the thread
    thread = get_object_or_404(Thread, pk=pk)

    # Check that it is assigned to the requester
    if thread.assignee != request.user and thread.assignee is not None:
        messages.error(request, "You cannot reply to someone else's thread!")
        return redirect("conversations:thread", pk=pk)

    # Get the category
    category_id = request.GET.get("category")
    if category_id is None:
        category = None
    else:
        # Ensure the id is a number
        try:
            category_id = int(category_id)
        except ValueError:
            messages.error(request, "Cannot change to invalid category")
            return redirect("conversations:thread", pk=pk)

        # Find the category
        category = get_object_or_404(Category, pk=category_id)

    # Set the new category
    thread.category = category
    thread.save()

    return redirect("conversations:thread", pk=pk)


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
        return redirect("conversations:thread", pk=pk)

    # Get the last message that was sent that wasn't from an @wafflehacks.tech email
    previous_messages = thread.message_set.all()
    last_message = previous_messages[0]
    for last_message in previous_messages:
        if "wafflehacks.tech" not in last_message.from_email:
            break

    # Render the template on initial request
    if request.method == "GET":
        return render(
            request,
            "conversations/reply.html",
            {"thread": thread, "last_message": last_message, "new_message": False},
        )

    # Get fields from request
    from_name = request.POST.get("name")
    from_email = request.POST.get("email")
    subject = request.POST.get("subject")
    html = request.POST.get("body")
    plaintext = request.POST.get("plaintext")

    # Get all the previous message ids for the References header
    message_ids = "\r\n".join([msg.message_id for msg in previous_messages.reverse()])

    # Queue the message for messages
    is_successful = mail.dispatch_message(
        request,
        from_name,
        from_email,
        f"{last_message.from_name} <{last_message.from_email}>",
        subject,
        html,
        plaintext,
        last_message.message_id,
        message_ids,
    )
    if not is_successful:
        return redirect("conversations:reply", pk=thread.pk)

    messages.success(
        request,
        "Successfully queued your reply for messages! "
        "It will be added below once it is successfully sent.",
    )
    return redirect("conversations:thread", pk=pk)


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
        return redirect("conversations:thread", pk=pk)

    # Delete the thread
    thread.delete()

    return redirect("conversations:index")


@login_required
def send(request):
    """
    Send a new message (starts a new thread)
    """
    if request.method == "GET":
        return render(request, "conversations/send.html", {"new_message": True})

    # Get fields from request
    from_name = request.POST.get("name")
    from_email = request.POST.get("email")
    to = request.POST.get("to")
    subject = request.POST.get("subject")
    html = request.POST.get("body")
    plaintext = request.POST.get("plaintext")

    # Queue the message for sending
    is_successful = mail.dispatch_message(
        request, from_name, from_email, to, subject, html, plaintext
    )
    if not is_successful:
        return redirect("conversations:send")

    messages.success(
        request,
        "Successfully queued your message for sending! "
        "It will be added below once it is successfully sent.",
    )
    return redirect("conversations:index")
