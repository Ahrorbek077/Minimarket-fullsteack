"""
History — AuditLog modeli.

Barcha muhim voqealar shu yerda saqlanadi:
  - User: create, update, soft_delete, login, logout
  - Product: create, update, soft_delete
  - Company/Branch: create, update, soft_delete
  - Purchase: create, receive, pay, cancel
  - Sale: checkout, return
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class AuditAction(models.TextChoices):
    # User
    LOGIN        = "login",         _("Tizimga kirdi")
    LOGOUT       = "logout",        _("Tizimdan chiqdi")
    # Universal CRUD
    CREATE       = "create",        _("Yaratildi")
    UPDATE       = "update",        _("Yangilandi")
    DELETE       = "delete",        _("O'chirildi")
    RESTORE      = "restore",       _("Qaytarildi")
    # Purchase
    PURCHASE_RECEIVED = "purchase_received", _("Xarid qabul qilindi")
    PURCHASE_PAID     = "purchase_paid",     _("Xarid to'lovi amalga oshdi")
    PURCHASE_CANCELLED= "purchase_cancelled",_("Xarid bekor qilindi")
    # Sale
    SALE_CHECKOUT = "sale_checkout", _("Sotuv yakunlandi")
    SALE_RETURN   = "sale_return",   _("Sotuv qaytarildi")
    # Stock
    STOCK_ADJUST  = "stock_adjust",  _("Ombor tuzatildi")


class AuditLog(models.Model):
    """
    O'zgarmas audit yozuvi.

    - BaseModel ishlatilmaydi (soft delete kerak emas — tarix o'chmasligi shart)
    - created_at bor, updated_at yo'q (yozuv o'zgarmasligi kerak)
    - changes: {field: [old_value, new_value]} — UPDATE uchun
    """
    user         = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="audit_logs",
        verbose_name=_("foydalanuvchi"),
    )
    action       = models.CharField(
        _("harakat"), max_length=30,
        choices=AuditAction.choices,
        db_index=True,
    )
    model_name   = models.CharField(
        _("model"), max_length=50, db_index=True,
        help_text="User, Product, Sale, Purchase ...",
    )
    object_id    = models.PositiveIntegerField(
        _("obyekt ID"), null=True, blank=True, db_index=True
    )
    object_repr  = models.CharField(
        _("obyekt nomi"), max_length=255,
        help_text="Masalan: 'Lipton choy 100g' yoki 'Ali Karimov'",
    )
    changes      = models.JSONField(
        _("o'zgarishlar"), default=dict, blank=True,
        help_text='{"field": ["eski qiymat", "yangi qiymat"]}',
    )
    ip_address   = models.GenericIPAddressField(
        _("IP manzil"), null=True, blank=True
    )
    extra        = models.JSONField(
        _("qo'shimcha ma'lumot"), default=dict, blank=True,
        help_text="Har qanday qo'shimcha context (invoice_no, amount...)",
    )
    created_at   = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name        = _("audit yozuvi")
        verbose_name_plural = _("audit yozuvlari")
        ordering            = ["-created_at"]
        indexes = [
            models.Index(fields=["model_name", "object_id"]),
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["action", "-created_at"]),
        ]

    def __str__(self) -> str:
        user = self.user.full_name if self.user else "Tizim"
        return f"[{self.action}] {self.model_name}#{self.object_id} — {user}"
