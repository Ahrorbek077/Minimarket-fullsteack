"""
User modellari.

CustomUser — email bilan login, role-based.
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class UserRole(models.TextChoices):
    """Foydalanuvchi rollari."""
    SUPER_ADMIN = "super_admin", _("Super Admin")
    ADMIN       = "admin",       _("Admin")
    CASHIER     = "cashier",     _("Kassir")
    STOREKEEPER = "storekeeper", _("Omborchi")
    ACCOUNTANT  = "accountant",  _("Buxgalter")


class UserLanguage(models.TextChoices):
    """Interfeys tillari."""
    UZ      = "uz",      "O'zbek (lotin)"
    UZ_CRYL = "uz_cryl", "Ўзбек (кирилл)"
    RU      = "ru",      "Русский"


class User(AbstractBaseUser, PermissionsMixin):
    """
    CustomUser modeli.

    - Email orqali login (username yo'q)
    - Role-based permissions
    - Soft delete (is_active=False)
    - Til tanlash
    """
    email       = models.EmailField(_("email"), unique=True, db_index=True)
    full_name   = models.CharField(_("to'liq ism"), max_length=150)
    phone       = models.CharField(_("telefon"), max_length=20, blank=True)
    avatar      = models.ImageField(
        _("rasm"), upload_to="avatars/", null=True, blank=True
    )
    role        = models.CharField(
        _("rol"), max_length=20,
        choices=UserRole.choices,
        default=UserRole.CASHIER,
        db_index=True,
    )
    language    = models.CharField(
        _("til"), max_length=10,
        choices=UserLanguage.choices,
        default=UserLanguage.UZ,
    )
    is_active   = models.BooleanField(_("faol"), default=True)
    is_staff    = models.BooleanField(_("xodim"), default=False)
    date_joined = models.DateTimeField(_("qo'shilgan"), default=timezone.now)

    # Soft delete uchun
    deleted_at  = models.DateTimeField(null=True, blank=True)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    objects     = UserManager()
    all_objects = models.Manager()   # o'chirilganlar ham

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        verbose_name        = _("foydalanuvchi")
        verbose_name_plural = _("foydalanuvchilar")
        ordering            = ["-date_joined"]

    def __str__(self) -> str:
        return f"{self.full_name} <{self.email}>"

    @property
    def is_super_admin(self) -> bool:
        return self.role == UserRole.SUPER_ADMIN

    @property
    def is_admin(self) -> bool:
        return self.role in {UserRole.SUPER_ADMIN, UserRole.ADMIN}

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self):
        """Foydalanuvchini o'chirish (deaktivatsiya)."""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_active", "deleted_at"])

    def restore(self):
        """O'chirilgan foydalanuvchini qaytarish."""
        self.is_active = True
        self.deleted_at = None
        self.save(update_fields=["is_active", "deleted_at"])

    def get_full_name(self) -> str:
        return self.full_name

    def get_short_name(self) -> str:
        return self.full_name.split()[0] if self.full_name else self.email
