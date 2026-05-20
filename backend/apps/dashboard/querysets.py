"""
Dashboard querysets — barcha statistika DB so'rovlari.
View dan ajratilgan, test qilish oson.
"""
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import (
    BooleanField, Count, DecimalField,
    ExpressionWrapper, F, Q, Sum,
)
from django.utils import timezone


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _date_range(period: str) -> tuple[date, date]:
    """
    Davr bo'yicha sana oralig'i.
    period: 'today' | 'week' | 'month' | 'year'
    """
    today = timezone.now().date()
    if period == "today":
        return today, today
    if period == "week":
        return today - timedelta(days=6), today
    if period == "month":
        return today.replace(day=1), today
    if period == "year":
        return today.replace(month=1, day=1), today
    return today, today


def _sales_agg(date_from: date, date_to: date) -> dict:
    """Sotuv aggregatsiyasi — berilgan davr uchun."""
    from datetime import datetime, time as dt_time
    from sales.models import PaymentMethod, Sale, SaleStatus

    # SQLite + USE_TZ=True da __date filter ishonchsiz.
    # UTC da hisoblash — make_aware UTC timezone bilan
    import pytz
    utc = pytz.UTC
    dt_from = datetime.combine(date_from, dt_time.min).replace(tzinfo=utc)
    dt_to   = datetime.combine(date_to,   dt_time.max).replace(tzinfo=utc)

    qs = Sale.objects.filter(
        deleted_at__isnull=True,
        status=SaleStatus.COMPLETED,
        created_at__gte=dt_from,
        created_at__lte=dt_to,
    )

    agg = qs.aggregate(
        total_sales   = Count("id"),
        total_revenue = Sum("net_amount"),
        total_discount= Sum("discount_amount"),
        total_debt    = Sum("debt_amount"),
        cash_total    = Sum("payments__amount",
            filter=Q(payments__method=PaymentMethod.CASH)),
        card_total    = Sum("payments__amount",
            filter=Q(payments__method=PaymentMethod.CARD)),
        debt_total    = Sum("payments__amount",
            filter=Q(payments__method=PaymentMethod.DEBT)),
    )

    # Foyda — SaleItem dan
    from sales.models import SaleItem
    profit_agg = SaleItem.objects.filter(
        deleted_at__isnull=True,
        sale__in=qs,
    ).aggregate(
        gross_profit=Sum(
            ExpressionWrapper(
                F("quantity") * (F("sell_price") - F("cost_price_snapshot")),
                output_field=DecimalField(),
            )
        )
    )

    def _d(val) -> str:
        return str(val or Decimal("0"))

    return {
        "sales_count":    agg["total_sales"]    or 0,
        "revenue":        _d(agg["total_revenue"]),
        "discount":       _d(agg["total_discount"]),
        "gross_profit":   _d(profit_agg["gross_profit"]),
        "debt":           _d(agg["total_debt"]),
        "cash":           _d(agg["cash_total"]),
        "card":           _d(agg["card_total"]),
        "debt_payments":  _d(agg["debt_total"]),
    }


# ─── Dashboard sections ────────────────────────────────────────────────────────

def get_period_stats(period: str) -> dict:
    """Bir davr uchun sotuv statistikasi."""
    d_from, d_to = _date_range(period)
    return {"period": period, "date_from": str(d_from), "date_to": str(d_to),
            **_sales_agg(d_from, d_to)}


def get_stock_overview() -> dict:
    """Ombor umumiy holati."""
    from inventory.models import Stock

    agg = Stock.objects.filter(
        product__deleted_at__isnull=True,
        product__is_active=True,
    ).aggregate(
        total_products  = Count("id"),
        low_stock       = Count("id", filter=Q(quantity__lte=F("product__min_stock"))),
        out_of_stock    = Count("id", filter=Q(quantity__lte=0)),
        total_cost_val  = Sum(
            ExpressionWrapper(
                F("quantity") * F("product__cost_price"),
                output_field=DecimalField(),
            )
        ),
        total_sell_val  = Sum(
            ExpressionWrapper(
                F("quantity") * F("product__sell_price"),
                output_field=DecimalField(),
            )
        ),
    )

    return {
        "total_products":  agg["total_products"]  or 0,
        "low_stock_count": agg["low_stock"]        or 0,
        "out_of_stock":    agg["out_of_stock"]     or 0,
        "cost_value":      str(agg["total_cost_val"]  or Decimal("0")),
        "sell_value":      str(agg["total_sell_val"]  or Decimal("0")),
    }


def get_debts_overview() -> dict:
    """Xarid qarzlari umumiy holati."""
    from purchases.models import Purchase, PurchaseStatus

    today = timezone.now().date()
    qs = Purchase.objects.filter(
        deleted_at__isnull=True,
        status__in=[PurchaseStatus.RECEIVED, PurchaseStatus.PARTIAL],
        debt_amount__gt=0,
    )
    agg = qs.aggregate(
        count        = Count("id"),
        total_debt   = Sum("debt_amount"),
        overdue_count= Count("id", filter=Q(
            due_date__isnull=False,
            due_date__lt=today,
        )),
        overdue_debt = Sum("debt_amount", filter=Q(
            due_date__isnull=False,
            due_date__lt=today,
        )),
    )
    return {
        "count":         agg["count"]         or 0,
        "total_debt":    str(agg["total_debt"]    or Decimal("0")),
        "overdue_count": agg["overdue_count"]  or 0,
        "overdue_debt":  str(agg["overdue_debt"]  or Decimal("0")),
    }


def get_top_products_today(limit: int = 5) -> list:
    """Bugungi eng ko'p sotilgan mahsulotlar."""
    from sales.models import SaleItem, SaleStatus

    today = timezone.now().date()
    return list(
        SaleItem.objects
        .filter(
            deleted_at__isnull=True,
            sale__status=SaleStatus.COMPLETED,
            sale__created_at__gte=timezone.make_aware(__import__('datetime').datetime.combine(today, __import__('datetime').time.min)),
            sale__created_at__lte=timezone.make_aware(__import__('datetime').datetime.combine(today, __import__('datetime').time.max)),
        )
        .values("product__id", "product__name")
        .annotate(
            total_qty     = Sum("quantity"),
            total_revenue = Sum(
                ExpressionWrapper(
                    F("quantity") * F("sell_price"),
                    output_field=DecimalField(),
                )
            ),
        )
        .order_by("-total_revenue")[:limit]
    )


def get_sales_chart(days: int = 7) -> list:
    """
    Oxirgi N kun uchun kunlik sotuv grafigi.
    Frontend chart uchun.
    """
    from django.db.models.functions import TruncDate
    from sales.models import Sale, SaleStatus

    date_from = timezone.now().date() - timedelta(days=days - 1)

    rows = (
        Sale.objects
        .filter(
            deleted_at__isnull=True,
            status=SaleStatus.COMPLETED,
            created_at__gte=__import__('django.utils.timezone', fromlist=['make_aware']).make_aware(
                __import__('datetime').datetime.combine(date_from, __import__('datetime').time.min)
            ),
        )
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(
            count   = Count("id"),
            revenue = Sum("net_amount"),
        )
        .order_by("day")
    )

    # Har bir kun bo'lishi kerak — bo'sh kunlar ham
    data_map = {str(r["day"]): r for r in rows}
    result   = []
    for i in range(days):
        d   = date_from + timedelta(days=i)
        key = str(d)
        row = data_map.get(key)
        result.append({
            "date":    key,
            "count":   row["count"]   if row else 0,
            "revenue": str(row["revenue"]) if row else "0",
        })
    return result


def get_recent_sales(limit: int = 5) -> list:
    """Oxirgi N ta sotuv — activity feed uchun."""
    from sales.models import Sale, SaleStatus

    return list(
        Sale.objects
        .filter(deleted_at__isnull=True, status=SaleStatus.COMPLETED)
        .select_related("cashier")
        .order_by("-created_at")[:limit]
        .values(
            "id", "invoice_no", "net_amount",
            "created_at", "cashier__full_name",
        )
    )


def get_low_stock_alerts(limit: int = 5) -> list:
    """Kam qoldiqli mahsulotlar — ogohlantirish."""
    from inventory.models import Stock

    return list(
        Stock.objects
        .filter(
            product__deleted_at__isnull=True,
            product__is_active=True,
            quantity__lte=F("product__min_stock"),
        )
        .select_related("product", "product__unit")
        .order_by("quantity")[:limit]
        .values(
            "product__id",
            "product__name",
            "product__unit__short_name",
            "quantity",
            "product__min_stock",
        )
    )
