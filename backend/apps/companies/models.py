"""
Companies modellari.

Company  — mahsulot yetkazib beruvchi kompaniya / zavod
Branch   — kompaniyaning filiallari
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class Company(BaseModel):
    """
    Yetkazib beruvchi kompaniya yoki zavod.

    Misol:
        Coca-Cola Uzbekistan (company)
        └── Toshkent filiali   (branch)
        └── Samarqand filiali  (branch)
    """
    name    = models.CharField(_("nomi"), max_length=200, db_index=True)
    phone   = models.CharField(_("telefon"), max_length=20, blank=True)
    address = models.TextField(_("manzil"), blank=True)
    inn     = models.CharField(
        _("INN"), max_length=20, blank=True,
        help_text="Soliq raqami"
    )
    note    = models.TextField(_("izoh"), blank=True)

    class Meta:
        verbose_name        = _("kompaniya")
        verbose_name_plural = _("kompaniyalar")
        ordering            = ["name"]

    def __str__(self) -> str:
        return self.name

    @property
    def branch_count(self) -> int:
        return self.branches.filter(deleted_at__isnull=True).count()

    @property
    def total_debt(self):
        """Kompaniyaga umumiy qarz."""
        from django.db.models import Sum
        # purchases app qo'shilgach ishlaydi
        result = self.purchases.filter(
            deleted_at__isnull=True
        ).aggregate(total=Sum("debt_amount"))
        return result["total"] or 0


class Branch(BaseModel):
    """
    Kompaniya filiasi.
    Xarid shu filialdan qilinadi.
    """
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="branches",
        verbose_name=_("kompaniya"),
    )
    name    = models.CharField(_("nomi"), max_length=200)
    phone   = models.CharField(_("telefon"), max_length=20, blank=True)
    address = models.TextField(_("manzil"), blank=True)
    note    = models.TextField(_("izoh"), blank=True)

    class Meta:
        verbose_name        = _("filial")
        verbose_name_plural = _("filiallar")
        ordering            = ["company__name", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "name"],
                condition=models.Q(deleted_at__isnull=True),
                name="unique_branch_name_per_company",
            )
        ]

    def __str__(self) -> str:
        return f"{self.company.name} — {self.name}"
