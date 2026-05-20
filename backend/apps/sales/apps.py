from django.apps import AppConfig


class SalesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sales"
    verbose_name = "Sotuvlar"

    def ready(self):
        import sales.signals  # noqa: F401
