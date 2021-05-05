from celery import Celery
from os import environ

# Set the settings module
environ.setdefault("DJANGO_SETTINGS_MODULE", "mailgunner.settings")

# Create the celery app
app = Celery("schedule")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
