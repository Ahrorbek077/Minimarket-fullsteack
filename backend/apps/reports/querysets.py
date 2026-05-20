"""
Reports querysets — hisobot uchun DB so'rovlar.
View va export logikasidan ajratilgan.
"""
from decimal import Decimal
from django.db.models import (
    BooleanField, Count, DecimalField, ExpressionWrapper, F,
    OuterRef, Q, Subquery, Sum, Value,
)
from django.db.models.functions import TruncDate, TruncMonth, TruncWeek
from django.utils import timezone


# ─── Sales ────────────────────────────────────────────────────────────────────

def get_sales_report(date_from, date_to):
    """
    Sotuvlar hisoboti — har bir sotuv qatori.
    """
    from sales.models import Sale, SaleStatus, PaymentMethod
    from django.db.models import Sum

    qs = (
        Sale.objects
        .filter(
            deleted_at__isnull=True,
            status=SaleStatus.COMPLETED,
            created_at__date__gte=date_from,
            created_at__date__lte=date_to,
        )
        .select_related("cashier")
        .prefetch_related("items__product", "payments")
        .order_by("created_at")
    )
    return qs


def get_sales_summary(date_from, date_to) -> dict:
    """
    Sotuvlar umumiy statistikasi.
    """
    from sales.models import Sale, SaleStatus, PaymentMethod

    qs = Sale.objects.filter(
        deleted_at__isnull=True,
        status=SaleStatus.COMPLETED,
        created_at__date__gte=date_from,
        created_at__date__lte=date_to,
    )
    agg = qs.aggregate(
        total_sales     = Count("id"),
        total_revenue   = Sum("net_amount"),
        total_discount  = Sum("discount_amount"),
        total_debt      = Sum("debt_amount"),
        cash_total      = Sum(
            "payments__amount",
            filter=Q(payments__method=PaymentMethod.CASH)
        ),
        card_total      = Sum(
            "payments__amount",
            filter=Q(payments__method=PaymentMethod.CARD)
        ),
        debt_total      = Sum(
            "payments__amount",
            filter=Q(payments__method=PaymentMethod.DEBT)
        ),
    )
    # Foyda hisoblash
    from sales.models import SaleItem
    profit_agg = SaleItem.objects.filter(
        sale__in=qs, deleted_at__isnull=True
    ).aggregate(
        total_cost  = Sum(
            ExpressionWrapper(
                F("quantity") * F("cost_price_snapshot"),
                output_field=DecimalField()
            )
        ),
        total_sell  = Sum(
            ExpressionWrapper(
                F("quantity") * F("sell_price"),
                output_field=DecimalField()
            )
        ),
    )
    cost  = profit_agg["total_cost"]  or Decimal("0")
    sell  = profit_agg["total_sell"]  or Decimal("0")

    return {
        "date_from":      str(date_from),
        "date_to":        str(date_to),
        "total_sales":    agg["total_sales"]    or 0,
        "total_revenue":  agg["total_revenue"]  or Decimal("0"),
        "total_discount": agg["total_discount"] or Decimal("0"),
        "total_debt":     agg["total_debt"]     or Decimal("0"),
        "cash_total":     agg["cash_total"]     or Decimal("0"),
        "card_total":     agg["card_total"]     or Decimal("0"),
        "debt_total":     agg["debt_total"]     or Decimal("0"),
        "gross_profit":   sell - cost,
        "profit_margin":  round(float((sell - cost) / sell * 100), 2) if sell else 0,
    }


def get_sales_by_period(date_from, date_to, period="daily"):
    """
    Sotuvlarni kun / hafta / oy bo'yicha guruhlash.
    period: daily | weekly | monthly
    """
    from sales.models import Sale, SaleStatus

    trunc_map = {
        "daily":   TruncDate,
        "weekly":  TruncWeek,
        "monthly": TruncMonth,
    }
    trunc_fn = trunc_map.get(period, TruncDate)

    # Profit ni SaleItem dan subquery bilan hisoblaymiz —
    # Sale dan items__ orqali JOIN qilganda grouping xato natija beradi
    from sales.models import SaleItem, SaleStatus as SS
    from django.db.models import OuterRef

    profit_subq = (
        SaleItem.objects
        .filter(sale=OuterRef("pk"), deleted_at__isnull=True)
        .values("sale")
        .annotate(
            total_profit=Sum(
                ExpressionWrapper(
                    F("quantity") * (F("sell_price") - F("cost_price_snapshot")),
                    output_field=DecimalField(),
                )
            )
        )
        .values("total_profit")
    )

    return (
        Sale.objects
        .filter(
            deleted_at__isnull=True,
            status=SaleStatus.COMPLETED,
            created_at__date__gte=date_from,
            created_at__date__lte=date_to,
        )
        .annotate(
            period      = trunc_fn("created_at"),
            sale_profit = Subquery(profit_subq[:1], output_field=DecimalField()),
        )
        .values("period")
        .annotate(
            count   = Count("id"),
            revenue = Sum("net_amount"),
            profit  = Sum("sale_profit"),
        )
        .order_by("period")
    )


# ─── Products ─────────────────────────────────────────────────────────────────

def get_top_products(date_from, date_to, limit=20):
    """
    Eng ko'p sotilgan mahsulotlar.
    """
    from sales.models import SaleItem, SaleStatus

    return (
        SaleItem.objects
        .filter(
            deleted_at__isnull=True,
            sale__status=SaleStatus.COMPLETED,
            sale__created_at__date__gte=date_from,
            sale__created_at__date__lte=date_to,
        )
        .values("product__id", "product__name", "product__unit__short_name")
        .annotate(
            total_qty     = Sum("quantity"),
            total_revenue = Sum(
                ExpressionWrapper(F("quantity") * F("sell_price"), output_field=DecimalField())
            ),
            total_profit  = Sum(
                ExpressionWrapper(
                    F("quantity") * (F("sell_price") - F("cost_price_snapshot")),
                    output_field=DecimalField()
                )
            ),
        )
        .order_by("-total_revenue")[:limit]
    )


def get_stock_report():
    """
    Joriy ombor holati.
    """
    from inventory.models import Stock
    from django.db.models import F

    return (
        Stock.objects
        .select_related("product", "product__category", "product__unit")
        .filter(product__deleted_at__isnull=True, product__is_active=True)
        .annotate(
            cost_value = ExpressionWrapper(
                F("quantity") * F("product__cost_price"),
                output_field=DecimalField()
            ),
            sell_value = ExpressionWrapper(
                F("quantity") * F("product__sell_price"),
                output_field=DecimalField()
            ),
            is_low_stock = ExpressionWrapper(
                Q(quantity__lte=F("product__min_stock")),
                output_field=BooleanField()
            ),
        )
        .order_by("product__name")
    )


def get_stock_summary() -> dict:
    from inventory.models import Stock
    from django.db.models import F

    agg = Stock.objects.filter(
        product__deleted_at__isnull=True
    ).aggregate(
        total_items      = Count("id"),
        total_cost_value = Sum(
            ExpressionWrapper(F("quantity") * F("product__cost_price"), output_field=DecimalField())
        ),
        total_sell_value = Sum(
            ExpressionWrapper(F("quantity") * F("product__sell_price"), output_field=DecimalField())
        ),
        low_stock_count  = Count("id", filter=Q(quantity__lte=F("product__min_stock"))),
        out_of_stock     = Count("id", filter=Q(quantity__lte=0)),
    )
    return {
        "total_items":       agg["total_items"]       or 0,
        "total_cost_value":  agg["total_cost_value"]  or Decimal("0"),
        "total_sell_value":  agg["total_sell_value"]  or Decimal("0"),
        "potential_profit":  (agg["total_sell_value"] or Decimal("0")) - (agg["total_cost_value"] or Decimal("0")),
        "low_stock_count":   agg["low_stock_count"]   or 0,
        "out_of_stock":      agg["out_of_stock"]      or 0,
    }


# ─── Purchases ────────────────────────────────────────────────────────────────

def get_purchases_report(date_from, date_to):
    from purchases.models import Purchase

    return (
        Purchase.objects
        .filter(
            deleted_at__isnull=True,
            created_at__date__gte=date_from,
            created_at__date__lte=date_to,
        )
        .select_related("company", "branch", "created_by")
        .prefetch_related("items__product", "payments")
        .order_by("created_at")
    )


def get_debt_report():
    """Hali to'lanmagan xarid qarzlari."""
    from purchases.models import Purchase, PurchaseStatus
    from django.utils import timezone

    return (
        Purchase.objects
        .filter(
            deleted_at__isnull=True,
            status__in=[PurchaseStatus.RECEIVED, PurchaseStatus.PARTIAL],
            debt_amount__gt=0,
        )
        .select_related("company", "branch")
        .order_by("due_date")
        .annotate(
            is_overdue=ExpressionWrapper(
                Q(due_date__lt=timezone.now().date()) & Q(due_date__isnull=False),
                output_field=BooleanField()
            )
        )
    )
