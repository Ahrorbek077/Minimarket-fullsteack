"""
Sales modellari.

Sale        — yakunlangan sotuv
SaleItem    — sotuvdagi har bir mahsulot qatori
SalePayment — to'lov (naqd / karta / nasiya) — aralash ham bo'ladi
"""
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class SaleStatus(models.TextChoices):
    COMPLETED = "completed", _("Yakunlandi")
    RETURNED  = "returned",  _("Qaytarildi")
    PARTIAL   = "partial",   _("Qisman qaytarildi")


class PaymentMethod(models.TextChoices):
    CASH  = "cash",  _("Naqd")
    CARD  = "card",  _("Karta")
    DEBT  = "debt",  _("Nasiya")


class Sale(BaseModel):
    """
    Yakunlangan sotuv.

    Har bir sotuv:
      - 1+ SaleItem
      - 1+ SalePayment (naqd, karta, nasiya — aralash)
      - Ixtiyoriy chegirma (%)
    """
    invoice_no   = models.CharField(
        _("chek raqami"), max_length=30,
        unique=True, db_index=True,
    )
    status       = models.CharField(
        _("holat"), max_length=20,
        choices=SaleStatus.choices,
        default=SaleStatus.COMPLETED,
        db_index=True,
    )
    total_amount = models.DecimalField(
        _("jami summa"), max_digits=16, decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    discount_pct = models.DecimalField(
        _("chegirma %"), max_digits=5, decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    discount_amount = models.DecimalField(
        _("chegirma summasi"), max_digits=16, decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    net_amount   = models.DecimalField(
        _("to'lanadigan summa"), max_digits=16, decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    paid_amount  = models.DecimalField(
        _("to'langan summa"), max_digits=16, decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    debt_amount  = models.DecimalField(
        _("nasiya qoldig'i"), max_digits=16, decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    cashier      = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="sales",
        verbose_name=_("kassir"),
    )
    note         = models.TextField(_("izoh"), blank=True)

    class Meta:
        verbose_name        = _("sotuv")
        verbose_name_plural = _("sotuvlar")
        ordering            = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["cashier", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"Sotuv #{self.invoice_no} | {self.net_amount}"

    @property
    def is_debt(self) -> bool:
        return self.debt_amount > 0

    @property
    def profit(self):
        """
        Sotuv foydasi.

        `prefetch_related("items")` bo'lsa — Python da filter qilinadi (N+1 yo'q).
        Bo'lmasa — bitta query ketadi.
        """
        try:
            # prefetch_related("items") bo'lsa _prefetched_objects_cache da bor
            items = [
                i for i in self.items.all()
                if i.deleted_at is None
            ]
        except Exception:
            items = list(self.items.filter(deleted_at__isnull=True))

        cost = sum(item.quantity * item.cost_price_snapshot for item in items)
        return self.net_amount - cost


class SaleItem(BaseModel):
    """Sotuvdagi har bir mahsulot qatori."""
    sale       = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("sotuv"),
    )
    product    = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="sale_items",
        verbose_name=_("mahsulot"),
    )
    quantity   = models.DecimalField(
        _("miqdor"), max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    sell_price = models.DecimalField(
        _("sotish narxi"), max_digits=14, decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Sotuv paytidagi narx (snapshot)",
    )
    cost_price_snapshot = models.DecimalField(
        _("tan narxi (snapshot)"), max_digits=14, decimal_places=2,
        default=0,
        help_text="Foyda hisoblash uchun saqlanadi",
    )
    total      = models.DecimalField(
        _("jami"), max_digits=16, decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name        = _("sotuv qatori")
        verbose_name_plural = _("sotuv qatorlari")

    def __str__(self) -> str:
        return f"{self.product.name} × {self.quantity}"


class SalePayment(BaseModel):
    """
    Sotuv uchun to'lov.
    Bir sotuv uchun bir nechta to'lov bo'lishi mumkin:
    masalan, 30 000 naqd + 20 000 karta.
    """
    sale   = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name=_("sotuv"),
    )
    method = models.CharField(
        _("to'lov usuli"), max_length=10,
        choices=PaymentMethod.choices,
    )
    amount = models.DecimalField(
        _("summa"), max_digits=16, decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name        = _("sotuv to'lovi")
        verbose_name_plural = _("sotuv to'lovlari")

    def __str__(self) -> str:
        return f"{self.get_method_display()} | {self.amount}"
