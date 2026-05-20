"""
Inventory modellari.

Stock         — har bir mahsulotning joriy qoldig'i (1:1)
StockMovement — har qanday harakatning tarixi (kirdi/chiqdi/qaytarish/tuzatish)
"""
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class Stock(models.Model):
    """
    Mahsulot qoldig'i — 1:1 Product bilan.

    BaseModel ishlatilmaydi — bu jadvalni o'chirish kerak bo'lmaydi,
    Product o'chirilsa signal orqali tozalanadi.
    """
    product  = models.OneToOneField(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="stock",
        verbose_name=_("mahsulot"),
    )
    quantity = models.DecimalField(
        _("miqdor"), max_digits=12, decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = _("qoldiq")
        verbose_name_plural = _("qoldiqlar")
        ordering            = ["product__name"]

    def __str__(self) -> str:
        return f"{self.product.name}: {self.quantity} {self.product.unit.short_name if self.product.unit else ''}"

    @property
    def is_low(self) -> bool:
        """Minimum qoldiqdan past yoki teng."""
        return self.quantity <= self.product.min_stock

    @property
    def is_empty(self) -> bool:
        return self.quantity <= 0


class MovementType(models.TextChoices):
    IN       = "in",       _("Kirdi")         # Xarid / qabul
    OUT      = "out",      _("Chiqdi")        # Sotuv
    RETURN_IN  = "return_in",  _("Qaytib keldi")  # Sotuvdan qaytarish → ombor
    RETURN_OUT = "return_out", _("Qaytarildi")    # Xariddan qaytarish → kompaniya
    ADJUST   = "adjust",   _("Tuzatish")      # Manual sozlash


class StockMovement(BaseModel):
    """
    Ombor harakati tarixi.

    Har bir IN/OUT/RETURN/ADJUST voqeasi shu yerga yoziladi.
    source_type + source_id — qaysi obyektdan kelgani (Purchase, Sale...)
    """
    product     = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="movements",
        verbose_name=_("mahsulot"),
    )
    movement_type = models.CharField(
        _("harakat turi"), max_length=15,
        choices=MovementType.choices,
        db_index=True,
    )
    quantity    = models.DecimalField(
        _("miqdor"), max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Har doim musbat son — yo'nalish movement_type dan aniqlanadi",
    )
    # Harakatdan oldin va keyin
    qty_before  = models.DecimalField(
        _("harakatdan oldin"), max_digits=12, decimal_places=2, default=0
    )
    qty_after   = models.DecimalField(
        _("harakatdan keyin"), max_digits=12, decimal_places=2, default=0
    )
    # Qaysi obyektga bog'liq (Purchase yoki Sale)
    source_type = models.CharField(
        _("manba turi"), max_length=50, blank=True,
        help_text="purchase | sale | manual"
    )
    source_id   = models.PositiveIntegerField(
        _("manba ID"), null=True, blank=True
    )
    reason      = models.CharField(
        _("sabab / izoh"), max_length=300, blank=True
    )
    created_by  = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="stock_movements",
        verbose_name=_("kim tomonidan"),
    )

    class Meta:
        verbose_name        = _("ombor harakati")
        verbose_name_plural = _("ombor harakatlari")
        ordering            = ["-created_at"]
        indexes = [
            models.Index(fields=["product", "-created_at"]),
            models.Index(fields=["movement_type", "-created_at"]),
            models.Index(fields=["source_type", "source_id"]),
        ]

    def __str__(self) -> str:
        return (
            f"{self.get_movement_type_display()} | "
            f"{self.product.name} | "
            f"{self.quantity}"
        )
