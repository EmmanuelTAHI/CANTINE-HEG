from django.apps import AppConfig


class CantineWebConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cantine_web"

    def ready(self):
        import cantine_web.signals
