from anymail.exceptions import (
    AnymailAPIError,
    AnymailInvalidAddress,
    AnymailRecipientsRefused,
)
from django.contrib import messages
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.core.mail import EmailMultiAlternatives
from email.utils import getaddresses
import magic
from pathlib import Path

HTML_EMAIL_FORMAT = (
    '<!doctype html><head><meta name="viewport" content="width=device-width"/>'
    '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>'
    "<title>{subject}</title></head><body>{html}</body></html>"
)


def format_address(parts):
    """
    Format a parsed email address for sending
    :param parts: a tuple of the name and email
    :return: a properly formatted email
    """
    if parts[0] == "":
        return parts[1]
    return f"{parts[0]} <{parts[1]}>"


def validate_fields(
    request,
    from_name: str,
    from_email: str,
    to: str,
    subject: str,
    html: str,
    plaintext: str,
):
    """
    Ensure the parameters are valid

    :param request: the Django request
    :param from_name: who the mail is from
    :param from_email: the address the mail is from
    :param to: who the mail is to
    :param subject: the subject of the message
    :param html: the html content of the message
    :param plaintext: the text only content of the message
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
        messages.error(request, "There must be a subject for your message")
        return False
    if html is None or plaintext is None:
        messages.error(request, "Your message must have some content")
        return False

    # Ensure the from email is valid
    if "@" in from_email:
        messages.error(
            request,
            f"Invalid username for the from email! Got {from_email}@wafflehacks.tech",
        )
        return False

    return True


def build_message(
    request,
    from_name: str,
    from_email: str,
    to: str,
    subject: str,
    html: str,
    plaintext: str,
    in_reply_to: str = None,
    references: str = None,
):
    """
    Create the multi-part message to be sent

    :param request: the Django request
    :param from_name: who the mail is from
    :param from_email: the address the mail is from
    :param to: who the mail is to
    :param subject: the subject of the message
    :param html: the html content of the message
    :param plaintext: the text only content of the message
    :param in_reply_to: what message the email is replying to
    :param references: other messages in the thread
    :return: the constructed message
    """
    # Parse the To email(s)
    addresses = getaddresses(to.split(","))
    formatted = list(map(format_address, addresses))

    # Build the message
    message = EmailMultiAlternatives(
        subject=subject,
        body=plaintext,
        from_email=f"{from_name} <{from_email}@wafflehacks.tech>",
        to=formatted,
    )
    message.attach_alternative(
        HTML_EMAIL_FORMAT.format(subject=subject, html=html), "text/html"
    )

    # Add reply headers
    if in_reply_to is not None and references is not None:
        message.extra_headers["In-Reply-To"] = in_reply_to
        message.extra_headers["References"] = references

    # Get and add attachments
    for file in request.FILES.values():
        # Determine the MIME type of the uploaded file and read the content
        if isinstance(file, TemporaryUploadedFile):
            mime = magic.from_file(file.temporary_file_path(), mime=True)
            path = Path(file.temporary_file_path())
            with path.open("rb") as f:
                content = f.read()
        else:
            content = file.read()
            mime = magic.from_buffer(content, mime=True)

        # Attach the file to the message
        message.attach(file.name, content, mime)

    return message


def dispatch_message(
    request,
    from_name: str,
    from_email: str,
    to: str,
    subject: str,
    html: str,
    plaintext: str,
    in_reply_to: str = None,
    references: str = None,
):
    """
    Dispatch a message through MailGun

    :param request: the Django request
    :param from_name: who the mail is from
    :param from_email: the address the mail is from
    :param to: who the mail is to
    :param subject: the subject of the message
    :param html: the html content of the message
    :param plaintext: the text only content of the message
    :param in_reply_to: what message the email is replying to
    :param references: other messages in the thread
    :return: whether the queuing was successful
    """
    if not validate_fields(
        request, from_name, from_email, to, subject, html, plaintext
    ):
        return False

    # Build the message
    message = build_message(
        request,
        from_name,
        from_email,
        to,
        subject,
        html,
        plaintext,
        in_reply_to,
        references,
    )

    # Queue the message for messages
    try:
        sent = message.send()
    except AnymailAPIError:
        messages.error(
            request,
            "An error occurred while messages your message. Please try again later.",
        )
        return False
    except AnymailInvalidAddress:
        messages.error(
            request,
            "Failed to parse emails to send to. Please check they are correct and try again.",
        )
        return False
    except AnymailRecipientsRefused:
        messages.error(
            request,
            "One or more of the recipients rejected the message. Please check they are correct and try again.",
        )
        return False

    # Ensure the message was sent
    if sent == 0:
        messages.error(
            request, "An error occurred while messages your message, please try again."
        )
        return False

    return True
