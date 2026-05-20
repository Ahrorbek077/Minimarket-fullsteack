"""
Custom User Manager.
"""
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Email-based user manager.
    create_user va create_superuser metodlari.
    """
    use_in_migrations = True

    def _create_user(self, email: str, password: str, **extra_fields):
        if not email:
            raise ValueError(_("Email majburiy."))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str = None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str, **extra_fields):
        from users.models import UserRole
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", UserRole.SUPER_ADMIN)

        if not extra_fields.get("is_staff"):
            raise ValueError(_("Superuser is_staff=True bo'lishi kerak."))
        if not extra_fields.get("is_superuser"):
            raise ValueError(_("Superuser is_superuser=True bo'lishi kerak."))

        return self._create_user(email, password, **extra_fields)

    def active(self):
        """Faqat faol foydalanuvchilar."""
        return self.filter(is_active=True, deleted_at__isnull=True)
