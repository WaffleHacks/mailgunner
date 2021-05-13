# Generated by Django 3.2.1 on 2021-05-08 03:07

from django.apps.registry import Apps
from django.conf import settings
from django.db import migrations


def create_profiles(apps: Apps, schema_editor):
    """
    Create profiles for all the non-discord users
    """
    Profile = apps.get_model("account", "Profile")
    User = apps.get_model(settings.AUTH_USER_MODEL)
    for user in User.objects.all():
        try:
            user.profile
        except Profile.DoesNotExist:
            profile = Profile(
                preferred_username=user.username.replace("#", "."), user=user
            )
            profile.save()


def remove_profiles(apps: Apps, schema_editor):
    """
    Remove the profiles for all non-discord users
    """
    Profile = apps.get_model("account", "Profile")
    for profile in Profile.objects.all():
        profile.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0001_initial"),
    ]

    operations = [migrations.RunPython(create_profiles, remove_profiles)]