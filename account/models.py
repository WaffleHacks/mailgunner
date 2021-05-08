from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    # The user it references
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # The user's preferred username
    # Used when composing or responding to a message
    preferred_username = models.CharField(max_length=150, blank=False, null=False)
