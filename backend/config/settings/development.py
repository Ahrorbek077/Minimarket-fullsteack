"""
Development settings — local muhit uchun.
"""
from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Development da pooling o'chirish (muammo bo'lishi mumkin)
DATABASES["default"]["OPTIONS"] = {}  # noqa: F405
DATABASES["default"]["CONN_MAX_AGE"] = 600  # noqa: F405

# Django Extensions
INSTALLED_APPS += ["django_extensions"]  # noqa: F405

# Email — consolega chiqarish
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Swagger hamma uchun ochiq
SPECTACULAR_SETTINGS = {  # noqa: F405
    **SPECTACULAR_SETTINGS,  # noqa: F405
    "SERVE_INCLUDE_SCHEMA": True,
}

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
