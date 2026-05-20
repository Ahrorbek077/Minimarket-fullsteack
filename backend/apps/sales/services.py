"""
Sales services — sotuv yaratish, qaytarish.

SaleService.checkout()  → Cartni yakunlash → Sale + SaleItem + SalePayment
SaleService.return_sale() → Sotuvni qaytarish → Stock qaytariladi
"""
import uuid
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from core.exceptions import BusinessLogicError
from inventory.services import StockService
from .cart import CartService
from .models import PaymentMethod, Sale, SaleItem, SalePayment, SaleStatus


def _generate_invoice_no() -> str:
    """Unikal chek raqami: INV-20240115-A3F2"""
    date_part = timezone.now().strftime("%Y%m%d")
    rand_part = uuid.uuid4().hex[:6].upper()
    return f"INV-{date_part}-{rand_part}"


class SaleService:

    # ── Checkout ──────────────────────────────────────────────────────────

    @staticmethod
    @transaction.atomic
    def checkout(
        user_id: int,
        payments: list[dict],
        discount_pct: Decimal = Decimal("0"),
        note: str = "",
        cashier=None,
    ) -> Sale:
        """
        Cartni yakunlash — sotuv yaratish.

        payments = [
          {"method": "cash",  "amount": "30000"},
          {"method": "card",  "amount": "20000"},
          {"method": "debt",  "amount": "10000"},
        ]

        Logika:
          1. Cartdan itemlarni olish
          2. Har bir item uchun stock tekshirish
          3. Sale + SaleItem + SalePayment yaratish
          4. StockService.deduct() — har item uchun
          5. Cartni tozalash
        """
        cart_data = CartService.get_cart(user_id)

        if not cart_data["items"]:
            raise BusinessLogicError("Cart bo'sh.", "empty_cart")

        if not payments:
            raise BusinessLogicError("Kamida bitta to'lov kerak.", "no_payment")

        # ── Summa hisoblash ───────────────────────────────────────────────
        total_amount = Decimal(str(cart_data["total_amount"]))

        discount_pct    = min(max(discount_pct, Decimal("0")), Decimal("100"))
        discount_amount = (total_amount * discount_pct / 100).quantize(Decimal("0.01"))
        net_amount      = total_amount - discount_amount

        # ── To'lovlarni tekshirish ─────────────────────────────────────────
        payments_total = sum(Decimal(str(p["amount"])) for p in payments)

        for p in payments:
            if Decimal(str(p["amount"])) <= 0:
                raise BusinessLogicError("To'lov summasi musbat bo'lishi kerak.", "invalid_payment")
            if p["method"] not in PaymentMethod.values:
                raise BusinessLogicError(f"Noto'g'ri to'lov usuli: {p['method']}", "invalid_method")

        if payments_total < net_amount:
            raise BusinessLogicError(
                f"To'lov yetarli emas. Kerak: {net_amount}, keldi: {payments_total}",
                "insufficient_payment",
            )

        paid_amount = net_amount
        debt_amount = Decimal("0")

        # Nasiya bo'lsa
        debt_payments = [p for p in payments if p["method"] == PaymentMethod.DEBT]
        if debt_payments:
            debt_amount = sum(Decimal(str(p["amount"])) for p in debt_payments)
            paid_amount = net_amount - debt_amount

        # ── Sale yaratish ──────────────────────────────────────────────────
        sale = Sale.objects.create(
            invoice_no      = _generate_invoice_no(),
            status          = SaleStatus.COMPLETED,
            total_amount    = total_amount,
            discount_pct    = discount_pct,
            discount_amount = discount_amount,
            net_amount      = net_amount,
            paid_amount     = paid_amount,
            debt_amount     = debt_amount,
            cashier         = cashier,
            note            = note,
        )

        # ── Barcha stock larni oldindan lock qilish (race condition yo'q) ──
        from products.models import Product
        from inventory.models import Stock

        product_ids = [item_data["product_id"] for item_data in cart_data["items"]]

        # Stock larni to'liq lock qilamiz — bir vaqtda ikki kassir
        # bir mahsulotni sota olmasin
        Stock.objects.select_for_update().filter(
            product_id__in=product_ids
        ).values_list("id", flat=True)   # lock qilish uchun evaluate

        # Product larni bir so'rovda olamiz
        products_map = {
            p.pk: p
            for p in Product.objects.select_for_update().filter(pk__in=product_ids)
        }

        # ── SaleItem + Stock deduct ────────────────────────────────────────
        for item_data in cart_data["items"]:
            product = products_map[item_data["product_id"]]
            qty     = Decimal(str(item_data["quantity"]))
            price   = Decimal(str(item_data["sell_price"]))

            SaleItem.objects.create(
                sale                = sale,
                product             = product,
                quantity            = qty,
                sell_price          = price,
                cost_price_snapshot = product.cost_price,
                total               = qty * price,
            )

            StockService.deduct(
                product     = product,
                quantity    = qty,
                source_type = "sale",
                source_id   = sale.pk,
                reason      = f"Sotuv #{sale.invoice_no}",
                created_by  = cashier,
            )

        # ── SalePayment ────────────────────────────────────────────────────
        for p in payments:
            SalePayment.objects.create(
                sale   = sale,
                method = p["method"],
                amount = Decimal(str(p["amount"])),
            )

        # ── Cart tozalash ──────────────────────────────────────────────────
        CartService.clear(user_id)

        return sale

    # ── Return ────────────────────────────────────────────────────────────

    @staticmethod
    @transaction.atomic
    def return_sale(
        sale: Sale,
        items_to_return: list[dict] | None = None,
        reason: str = "",
        cashier=None,
    ) -> Sale:
        """
        Sotuvni qaytarish — to'liq yoki qisman.

        items_to_return = None          → to'liq qaytarish
        items_to_return = [
          {"sale_item_id": 1, "quantity": 2},
        ]                               → qisman qaytarish
        """
        if sale.status == SaleStatus.RETURNED:
            raise BusinessLogicError("Sotuv allaqachon qaytarilgan.", "already_returned")

        sale_items = sale.items.filter(deleted_at__isnull=True).select_related("product")

        if items_to_return is None:
            # To'liq qaytarish
            return_list = [
                {"item": item, "quantity": item.quantity}
                for item in sale_items
            ]
            new_status = SaleStatus.RETURNED
        else:
            # Qisman qaytarish — validatsiya
            return_list = []
            for ret in items_to_return:
                item = sale_items.filter(pk=ret["sale_item_id"]).first()
                if not item:
                    raise BusinessLogicError(
                        f"SaleItem #{ret['sale_item_id']} topilmadi.", "not_found"
                    )
                qty = Decimal(str(ret["quantity"]))
                if qty <= 0 or qty > item.quantity:
                    raise BusinessLogicError(
                        f"Noto'g'ri qaytarish miqdori: {qty}.", "invalid_quantity"
                    )
                return_list.append({"item": item, "quantity": qty})
            new_status = SaleStatus.PARTIAL

        # Stock qaytarish
        for ret in return_list:
            StockService.return_to_stock(
                product     = ret["item"].product,
                quantity    = ret["quantity"],
                source_type = "sale",
                source_id   = sale.pk,
                reason      = f"Qaytarish #{sale.invoice_no}: {reason}",
                created_by  = cashier,
            )

        sale.status = new_status
        if reason:
            sale.note = f"{sale.note}\n[Qaytarish: {reason}]".strip()
        sale.save(update_fields=["status", "note"])
        return sale

    # ── Queries ───────────────────────────────────────────────────────────

    @staticmethod
    def get_queryset():
        return (
            Sale.objects
            .filter(deleted_at__isnull=True)
            .select_related("cashier")
            .prefetch_related("items__product", "payments")
            .order_by("-created_at")
        )

    @staticmethod
    def get_daily_summary(date=None):
        """Kunlik sotuv statistikasi."""
        from django.db.models import Count, Q, Sum
        if date is None:
            date = timezone.now().date()

        qs = Sale.objects.filter(
            created_at__date=date,
            deleted_at__isnull=True,
            status=SaleStatus.COMPLETED,
        )
        agg = qs.aggregate(
            total_sales   = Count("id"),
            total_revenue = Sum("net_amount"),
            total_cash    = Sum("payments__amount",
                filter=Q(payments__method=PaymentMethod.CASH)),
            total_card    = Sum("payments__amount",
                filter=Q(payments__method=PaymentMethod.CARD)),
            total_debt    = Sum("debt_amount"),
        )
        return {
            "date":          str(date),
            "total_sales":   agg["total_sales"]   or 0,
            "total_revenue": agg["total_revenue"] or 0,
            "total_cash":    agg["total_cash"]    or 0,
            "total_card":    agg["total_card"]    or 0,
            "total_debt":    agg["total_debt"]    or 0,
        }
