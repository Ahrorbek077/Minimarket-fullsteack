"""
Purchases modellari.

Purchase      — kompaniyadan qilingan xarid
PurchaseItem  — xariddagi har bir mahsulot qatori
PurchasePayment — qarzni to'lash tarixi
"""
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class PurchaseStatus(models.TextChoices):
    DRAFT    = "draft",    _("Qoralama")      # Hali tasdiqlanmagan
    RECEIVED = "received", _("Qabul qilindi") # Omborda, to'lov kutilmoqda
    PARTIAL  = "partial",  _("Qisman to'landi")
    PAID     = "paid",     _("To'liq to'landi")
    CANCELLED = "cancelled", _("Bekor qilindi")


class Purchase(BaseModel):
    """
    Kompaniyadan qilingan xarid.

    Flow:
      1. Purchase yaratiladi (draft)
      2. receive() → mahsulotlar omborga tushadi, status=received
      3. pay() → qarz kamayadi, status=partial yoki paid
    """
    company     = models.ForeignKey(
        "companies.Company",
        on_delete=models.PROTECT,
        related_name="purchases",
        verbose_name=_("kompaniya"),
    )
    branch      = models.ForeignKey(
        "companies.Branch",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="purchases",
        verbose_name=_("filial"),
    )
    invoice_no  = models.CharField(
        _("hisob-faktura raqami"), max_length=100,
        blank=True, db_index=True,
    )
    status      = models.CharField(
        _("holat"), max_length=20,
        choices=PurchaseStatus.choices,
        default=PurchaseStatus.DRAFT,
        db_index=True,
    )
    total_amount = models.DecimalField(
        _("jami summa"), max_digits=16, decimal_places=2, default=0,
        validators=[MinValueValidator(0)],
    )
    paid_amount  = models.DecimalField(
        _("to'langan summa"), max_digits=16, decimal_places=2, default=0,
        validators=[MinValueValidator(0)],
    )
    debt_amount  = models.DecimalField(
        _("qarz"), max_digits=16, decimal_places=2, default=0,
        validators=[MinValueValidator(0)],
    )
    due_date    = models.DateField(
        _("to'lov muddati"), null=True, blank=True,
        help_text="15, 30 kun yoki istalgan sana",
    )
    received_at = models.DateTimeField(
        _("qabul qilingan vaqt"), null=True, blank=True
    )
    note        = models.TextField(_("izoh"), blank=True)
    created_by  = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="purchases",
        verbose_name=_("kim tomonidan"),
    )

    class Meta:
        verbose_name        = _("xarid")
        verbose_name_plural = _("xaridlar")
        ordering            = ["-created_at"]

    def __str__(self) -> str:
        return f"Xarid #{self.pk} | {self.company.name} | {self.total_amount}"

    @property
    def is_fully_paid(self) -> bool:
        return self.debt_amount <= 0

    @property
    def is_overdue(self) -> bool:
        from django.utils import timezone
        if self.due_date and not self.is_fully_paid:
            return self.due_date < timezone.now().date()
        return False


class PurchaseItem(BaseModel):
    """
    Xariddagi mahsulot qatori.
    Har bir qator ombordagi mahsulotga bog'liq.
    """
    purchase    = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("xarid"),
    )
    product     = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="purchase_items",
        verbose_name=_("mahsulot"),
    )
    quantity    = models.DecimalField(
        _("miqdor"), max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    cost_price  = models.DecimalField(
        _("tan narxi"), max_digits=14, decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Ushbu xarid narxi",
    )
    sell_price  = models.DecimalField(
        _("sotish narxi"), max_digits=14, decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Xarid paytida belgilangan sotish narxi",
    )
    total       = models.DecimalField(
        _("jami"), max_digits=16, decimal_places=2, default=0,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name        = _("xarid qatori")
        verbose_name_plural = _("xarid qatorlari")

    def __str__(self) -> str:
        return f"{self.product.name} × {self.quantity}"

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.cost_price
        super().save(*args, **kwargs)


class PurchasePayment(BaseModel):
    """
    Xarid qarzini to'lash tarixi.
    Har bir to'lov alohida yozuv — tarix saqlanadi.
    """
    purchase   = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name=_("xarid"),
    )
    amount     = models.DecimalField(
        _("to'lov summasi"), max_digits=16, decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    note       = models.TextField(_("izoh"), blank=True)
    paid_by    = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_("kim to'ladi"),
    )

    class Meta:
        verbose_name        = _("to'lov")
        verbose_name_plural = _("to'lovlar")
        ordering            = ["-created_at"]

    def __str__(self) -> str:
        return f"To'lov {self.amount} | Xarid #{self.purchase_id}"
