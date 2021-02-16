from django.apps import AppConfig


class IncomingConfig(AppConfig):
    name = "conversations"

    def ready(self):
        """
        Register the signal for inbound messages
        """
        from . import signals  # noqa
