"""
Test settings — pytest uchun.
"""
from .base import *  # noqa: F401, F403

DEBUG = False
ALLOWED_HOSTS = ["*"]   # Test muhitida hamma domenga ruxsat
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Test uchun SQLite (tez ishlaydi)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Cache — locmem (Redis kerak emas testda)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Celery — sinxron rejimda
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Email
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Media test uchun
DEFAULT_FILE_STORAGE = "django.core.files.storage.InMemoryStorage"
