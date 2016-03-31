from django.apps import AppConfig


class WotConfig(AppConfig):
    name = 'wot_app'
    verbose_name = 'WoT Platform Application'

    def ready(self):
        from . import signals