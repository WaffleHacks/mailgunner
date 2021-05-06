# Generated by Django 3.2.1 on 2021-05-06 19:14

from django.apps.registry import Apps
from django.db import migrations


def remove_claims(apps: Apps, schema_editor):
    """
    Remove all the claimed threads due to migration to Discord authentication
    """
    Thread = apps.get_model("conversations", "Thread")
    for thread in Thread.objects.all():
        thread.assignee = None
        thread.save()


class Migration(migrations.Migration):

    dependencies = [
        ("conversations", "0018_message_status"),
    ]

    operations = [migrations.RunPython(remove_claims)]
