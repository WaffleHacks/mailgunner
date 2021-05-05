from anymail.signals import (
    AnymailInboundEvent,
    AnymailTrackingEvent,
    inbound,
    post_send,
    tracking,
)
from anymail.inbound import AnymailInboundMessage
from anymail.message import AnymailStatus
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.dispatch import receiver
from django.utils import timezone
from email.utils import getaddresses
from itertools import chain
import magic
from pathlib import Path

from .models import Category, Message, MessageStatus, MessageType, Thread


def create_thread(message: Message):
    """
    Create a new thread for a message
    """
    # Attempt to get a category for the thread
    try:
        category = Category.objects.get(addresses__contains=[message.from_email])
    except Category.DoesNotExist:
        category = None

    # Create and save the thread to the database
    thread = Thread(
        subject=message.subject,
        last_updated=message.timestamp,
        originally_from=f"{message.from_name} <{message.from_email}>",
        recipient=message.recipient_email,
        unread=True,
        category=category,
    )
    thread.save()

    # Add the message to it
    thread.message_set.add(message)


def stringify_parsed_email(parsed):
    """
    Convert a parsed email tuple into a single email string
    """
    if len(parsed) == 2:
        return f"{parsed[0]} <{parsed[1]}>"
    return parsed[0]


def associate_with_thread(message: Message, in_reply_to: str):
    """
    Attempt to associate a message with an existing thread or create a new thread
    """
    if in_reply_to is not None:
        try:
            # Find the parent message
            parent = Message.objects.get(message_id=in_reply_to)

            # Add the new message to the set
            parent.thread.last_updated = message.timestamp
            parent.thread.unread = True
            parent.thread.message_set.add(message)

            # Update both thread and message
            parent.thread.save()
            message.save()
        except Message.DoesNotExist:
            # Create an empty thread if one could not be found
            create_thread(message)

    # Create a new thread if no reply
    else:
        create_thread(message)


@receiver(inbound)
def inbound_handler(event: AnymailInboundEvent, esp_name: str, **_unused):
    """
    Receive inbound messages from MailGun
    """
    assert esp_name == "Mailgun"

    # TODO: prevent reset emails from being stored

    # Extract data from the message
    message = event.message  # type: AnymailInboundMessage
    received = Message(
        type=MessageType.INCOMING,
        sender_email=message.envelope_sender,
        recipient_email=message.envelope_recipient,
        from_name=message.from_email.display_name,
        from_email=message.from_email.addr_spec,
        to=", ".join(map(str, message.to)),
        cc=", ".join(map(str, message.cc)),
        subject=message.subject,
        timestamp=event.timestamp,
        text=message.text,
        html=message.html if message.html is not None else f"<pre>{message.text}</pre>",
        message_id=message["message-id"],
    )

    # Save message to database
    received.save()

    # Attempt to associate with existing thread
    associate_with_thread(received, message["in-reply-to"])

    # Extract the attachments (inline and direct)
    for attachment in chain(message.attachments, message.inline_attachments.values()):
        # Check the MIME type
        file = attachment.as_uploaded_file()
        mime = magic.from_buffer(file.read(), mime=True)

        # Get only the filename, not file path
        name = Path(attachment.get_filename()).name

        # Add it to the message
        received.attachment_set.create(
            name=name,
            content_type=mime,
            inline=attachment.is_inline_attachment(),
            content=file,
        )


@receiver(post_send)
def post_send_handler(
    message: EmailMessage, status: AnymailStatus, esp_name: str, **_unused
):
    """
    Add sent messages to their corresponding thread
    """
    assert esp_name == "Mailgun"

    # Parse the emails
    [(from_name, from_email)] = getaddresses([message.from_email])
    [(_, recipient_email), *_] = getaddresses(message.to)

    # Get the HTML message if it exists
    html = None
    if isinstance(message, EmailMultiAlternatives):
        # Get the html content
        for data, content_type in message.alternatives:
            if content_type == "text/html":
                html = data

    # Set the html content if there's nothing
    if html is None:
        html = f"<pre>{message.body}</pre>"

    # Extract data from the message
    sent = Message(
        type=MessageType.OUTGOING,
        sender_email=from_email,
        recipient_email=recipient_email,
        from_name=from_name,
        from_email=from_email,
        to=", ".join(message.to),
        cc=", ".join(message.cc),
        subject=message.subject,
        timestamp=timezone.now(),
        text=message.body,
        html=html,
        message_id=status.message_id,
        status=MessageStatus.PENDING,
    )

    # Save message to database
    sent.save()

    # Attempt to associate with existing thread
    associate_with_thread(
        sent,
        message.extra_headers.get("in-reply-to")
        or message.extra_headers.get("In-Reply-To"),
    )

    # Extract attachments
    for attachment in message.attachments:
        # Extract the attachment details
        # The MIME type can be trusted since it was already sniffed by the handler
        name, content, mime = attachment

        # Get only the filename, not the path
        sanitized_name = Path(name).name

        # Create a temporary file to be uploaded
        temp = TemporaryUploadedFile(name, mime, len(content), "utf-8")
        if type(content) == str:
            temp.write(content.encode())
        else:
            temp.write(content)

        # Add it to the message
        sent.attachment_set.create(
            name=sanitized_name,
            content_type=mime,
            inline=False,
            content=temp,
        )


@receiver(tracking)
def tracking_handler(event: AnymailTrackingEvent, esp_name: str, **_unused):
    """
    Update the current status of the message in the database
    """
    assert esp_name == "Mailgun"

    # Ensure the event is handleable
    if event.event_type not in ["delivered", "rejected", "bounced"]:
        return

    # Find the message in the database
    message = Message.objects.filter(message_id=event.message_id).get()

    # Modify the message
    message.status = {
        "delivered": MessageStatus.SENT,
        "rejected": MessageStatus.FAILED,
        "bounced": MessageStatus.FAILED,
    }[event.event_type]
    message.save()
