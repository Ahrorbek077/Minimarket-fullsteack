"""
Products modellari.

Category  — ichma-ich kategoriya daraxti
Unit      — o'lchov birliklari (dona, kg, litr, metr...)
Product   — mahsulot (barcode, narx, rasm, ...)
"""
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


# ─── Category ─────────────────────────────────────────────────────────────────

class Category(BaseModel):
    """
    Mahsulot kategoriyasi — ichma-ich (tree) tuzilma.

    Misol:
        Oziq-ovqat
        └── Sut mahsulotlari
            └── Pishloq
    """
    name   = models.CharField(_("nomi"), max_length=100)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="children",
        verbose_name=_("ota kategoriya"),
    )
    icon   = models.CharField(
        _("ikonka"), max_length=50, blank=True,
        help_text="Emoji yoki icon nomi. Masalan: 🥛"
    )
    order  = models.PositiveSmallIntegerField(_("tartib"), default=0)

    class Meta:
        verbose_name        = _("kategoriya")
        verbose_name_plural = _("kategoriyalar")
        ordering            = ["order", "name"]

    def __str__(self) -> str:
        if self.parent:
            return f"{self.parent} → {self.name}"
        return self.name

    @property
    def is_root(self) -> bool:
        """Ota kategoriyasi yo'q — daraxt ildizi."""
        return self.parent_id is None

    def get_ancestors(self) -> list:
        """Barcha ota-bobolarni qaytaradi."""
        ancestors = []
        current = self
        while current.parent:
            current = current.parent
            ancestors.insert(0, current)
        return ancestors


# ─── Unit ─────────────────────────────────────────────────────────────────────

class Unit(BaseModel):
    """
    O'lchov birligi.

    Misol: dona, kg, g, litr, ml, metr, sm
    """
    name       = models.CharField(_("nomi"), max_length=50, unique=True)
    short_name = models.CharField(
        _("qisqa nomi"), max_length=10,
        help_text="Masalan: dona → d, kilogram → kg"
    )

    class Meta:
        verbose_name        = _("o'lchov birligi")
        verbose_name_plural = _("o'lchov birliklari")
        ordering            = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.short_name})"


# ─── Product ──────────────────────────────────────────────────────────────────

class Product(BaseModel):
    """
    Mahsulot modeli.

    - barcode: scanner bilan o'qiladi
    - cost_price: sotib olish narxi
    - sell_price: sotish narxi (default; xaridda o'zgarishi mumkin)
    - min_stock: minimum qoldiq (bu miqdordan pastga tushsa ogohlantirish)
    """
    name        = models.CharField(_("nomi"), max_length=200, db_index=True)
    barcode     = models.CharField(
        _("barcode / QR"), max_length=100,
        unique=True, null=True, blank=True,
        db_index=True,
        help_text="EAN-13, EAN-8, QR code..."
    )
    category    = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="products",
        verbose_name=_("kategoriya"),
    )
    unit        = models.ForeignKey(
        Unit,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="products",
        verbose_name=_("o'lchov birligi"),
    )
    cost_price  = models.DecimalField(
        _("tan narxi"), max_digits=14, decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Oxirgi xarid narxi"
    )
    sell_price  = models.DecimalField(
        _("sotish narxi"), max_digits=14, decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    image       = models.ImageField(
        _("rasm"), upload_to="products/", null=True, blank=True
    )
    description = models.TextField(_("tavsif"), blank=True)
    min_stock   = models.DecimalField(
        _("minimum qoldiq"), max_digits=12, decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Bu miqdordan pastga tushsa ogohlantirish yuboriladi"
    )
    is_active   = models.BooleanField(
        _("faol"), default=True,
        help_text="Faol bo'lmagan mahsulot sotilmaydi"
    )

    class Meta:
        verbose_name        = _("mahsulot")
        verbose_name_plural = _("mahsulotlar")
        ordering            = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["barcode"]),
            models.Index(fields=["is_active", "deleted_at"]),
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def profit_margin(self) -> float:
        """Foydalilik % — sell_price / cost_price."""
        if self.cost_price and self.cost_price > 0:
            return round(
                float((self.sell_price - self.cost_price) / self.cost_price * 100), 2
            )
        return 0.0

    @property
    def profit_amount(self):
        """Har birlik uchun foyda summasi."""
        return self.sell_price - self.cost_price
