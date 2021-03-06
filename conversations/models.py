from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy
from django_better_admin_arrayfield.models.fields import ArrayField
from os import path
from uuid import uuid4


class Category(models.Model):
    """
    A collection of threads linked by recipient email
    """

    # The name of the category
    name = models.CharField(max_length=256)

    # The address corresponding to the field
    addresses = ArrayField(models.EmailField(), blank=True)

    def __str__(self):
        return self.name


class Thread(models.Model):
    """
    A chain of replies for messages linked by the 'References', 'Message-Id', and 'In-Reply-To' headers
    """

    # Who the thread is assigned to
    assignee = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, blank=True, null=True
    )

    # The category the message is in
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, blank=True, null=True
    )

    # The subject line of the original message
    subject = models.CharField(max_length=255)

    # When the thread last got a message
    last_updated = models.DateTimeField()

    # Who the message was originally from (ignores replies)
    originally_from = models.CharField(max_length=510)

    # Who the message was originally to (ignores replies)
    recipient = models.EmailField()

    # Whether the are any parts of the thread that are unread
    unread = models.BooleanField()

    def __str__(self):
        return f'<Thread pk={self.pk} originally_from="{self.originally_from}" last_updated="{self.recipient}"'

    def is_older_than_a_day(self):
        """
        Whether the message is older than a day
        """
        difference = timezone.now() - self.last_updated
        return difference.days >= 1

    class Meta:
        ordering = ["-last_updated"]


class MessageType(models.IntegerChoices):
    """
    The type of message
    """

    INCOMING = 0
    OUTGOING = 1


class MessageStatus(models.IntegerChoices):
    """
    The status of the message as reported by MailGun
    """

    PENDING = 0, gettext_lazy("Waiting to send...")
    SENT = 1, gettext_lazy("Successfully sent")
    FAILED = 2, gettext_lazy("Failed to send")

    __empty__ = gettext_lazy("N/A")


class Message(models.Model):
    """
    A message that was either sent or received
    """

    # The type of message
    type = models.IntegerField(choices=MessageType.choices)

    # The actual sender and recipient email
    sender_email = models.EmailField()
    recipient_email = models.EmailField()

    # The name and email as parsed from the 'From' header
    from_name = models.CharField(max_length=255)
    from_email = models.EmailField()

    # A concatenated string of recipients as parsed from the 'To' header(s)
    to = models.TextField()

    # A concatenated string of copies as parsed from the 'CC' header(s)
    cc = models.TextField(blank=True)

    # The subject of the email
    subject = models.CharField(max_length=255)

    # When the message was received
    timestamp = models.DateTimeField()

    # The content of the message in plain text and HTML form
    text = models.TextField()
    html = models.TextField()

    # The message ID and optionally the corresponding message for creating threads
    message_id = models.CharField(max_length=256)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, blank=True, null=True)

    # The current status of the message as reported by MailGun
    status = models.IntegerField(choices=MessageStatus.choices, null=True)

    def __str__(self):
        return f'<Message pk={self.pk} sender_email="{self.sender_email}" timestamp="{self.timestamp}">'

    def is_older_than_a_day(self):
        """
        Whether the message is older than a day
        """
        difference = timezone.now() - self.timestamp
        return difference.days >= 1

    def get_status(self):
        """
        Convert the status integer to a human readable value
        """
        return MessageStatus(self.status).label if self.status is not None else None

    class Meta:
        ordering = ["-timestamp"]


def upload_to_location(_instance, _filename):
    """
    Generate the path in S3 to store the files
    """
    return path.join("attachments", str(uuid4()))


class Attachment(models.Model):
    """
    An attachment on an conversations email
    """

    # The corresponding email
    message = models.ForeignKey(Message, on_delete=models.CASCADE)

    # The name of the file
    name = models.CharField(max_length=255)

    # The type of the content
    content_type = models.CharField(max_length=129)

    # Whether the attachment was inline
    inline = models.BooleanField()

    # The reference to the attachment content in S3
    # Generates a new UUID for the file to prevent collisions
    content = models.FileField(upload_to=upload_to_location)

    def __str__(self):
        return f'<Attachment name="{self.name}" type="{self.content_type}">'
