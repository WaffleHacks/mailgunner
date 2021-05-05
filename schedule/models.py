from django.db import models
from django.utils import timezone
from os import path
from uuid import uuid4


class Message(models.Model):
    """
    A message that is scheduled to be sent at sometime in the future
    """

    # Who the email is from
    from_name = models.CharField(max_length=255)
    from_email = models.EmailField()

    # Who the email should be sent to
    to = models.TextField()

    # The subject of the email
    subject = models.CharField(max_length=255)

    # The contents of the message in plain text and HTML
    text = models.TextField()
    html = models.TextField()

    # When the message should be sent
    send_at = models.DateTimeField()

    def __str__(self):
        return f'<ScheduledMessage pk={self.pk} from="{self.from_name} <{self.from_email}>" send_at={self.send_at}>'

    def was_sent(self):
        """
        Whether the message has already been sent
        """
        return timezone.now() >= self.send_at

    class Meta:
        ordering = ["send_at"]


def upload_to_location(_instance, _filename):
    """
    Generate the path in S3 to store the files
    """
    return path.join("schedule", str(uuid4()))


class Attachment(models.Model):
    """
    An attachment on a message
    """

    # The corresponding message
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
