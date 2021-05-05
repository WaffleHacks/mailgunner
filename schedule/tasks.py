from anymail.exceptions import (
    AnymailAPIError,
    AnymailInvalidAddress,
    AnymailRecipientsRefused,
)
from celery import shared_task
from logging import getLogger

from utils import mail
from .models import Message


@shared_task
def queue_message(message_id):
    logger = getLogger(f"{__name__}.queue_message")

    # Fetch the message
    try:
        message = Message.objects.filter(pk=message_id).get()
    except Message.DoesNotExist:
        logger.error(f"Message ({message_id}) no longer exists")
        return

    # Get the required info

    # Build the mime message
    attachments = map(lambda a: a.content, message.attachment_set.all())
    email = mail.build_message(
        attachments,
        message.from_name,
        message.from_email,
        message.to,
        message.subject,
        message.html,
        message.text,
    )

    # Send the message
    try:
        sent = email.send()
    except AnymailAPIError as e:
        logger.error(
            f"An API error occurred while attempting to send message {message_id}",
            exc_info=e,
        )
    except AnymailInvalidAddress as e:
        logger.error(
            f"Failed to parse emails to send to for message {message_id}", exc_info=e
        )
    except AnymailRecipientsRefused as e:
        logger.error(
            f"One or more recipients rejected message {message_id}", exc_info=e
        )
    else:
        if sent == 0:
            logger.error(
                f"An unknown error occurred while sending message {message_id}"
            )
        else:
            logger.info(f"Successfully sent schedule message {message_id}")
