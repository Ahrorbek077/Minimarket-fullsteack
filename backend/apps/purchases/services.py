"""
Purchases services — barcha biznes logika.

PurchaseService.create()   → Draft xarid yaratish
PurchaseService.receive()  → Qabul qilish → omborga tushirish
PurchaseService.pay()      → Qarz to'lash
PurchaseService.cancel()   → Bekor qilish
"""
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from core.exceptions import BusinessLogicError
from inventory.services import StockService
from .models import Purchase, PurchaseItem, PurchasePayment, PurchaseStatus


class PurchaseService:

    # ── Create ────────────────────────────────────────────────────────────

    @staticmethod
    @transaction.atomic
    def create(
        company,
        items_data: list[dict],
        branch=None,
        invoice_no: str = "",
        due_date=None,
        note: str = "",
        created_by=None,
    ) -> Purchase:
        """
        Yangi xarid yaratish (draft holat).

        items_data = [
          {"product": <Product>, "quantity": 10, "cost_price": 5000, "sell_price": 7000},
          ...
        ]
        """
        if not items_data:
            raise BusinessLogicError("Kamida bitta mahsulot bo'lishi kerak.", "empty_items")

        purchase = Purchase.objects.create(
            company    = company,
            branch     = branch,
            invoice_no = invoice_no,
            due_date   = due_date,
            note       = note,
            created_by = created_by,
            status     = PurchaseStatus.DRAFT,
        )

        total = Decimal("0")
        for item_data in items_data:
            qty        = Decimal(str(item_data["quantity"]))
            cost_price = Decimal(str(item_data["cost_price"]))
            sell_price = Decimal(str(item_data["sell_price"]))

            PurchaseItem.objects.create(
                purchase   = purchase,
                product    = item_data["product"],
                quantity   = qty,
                cost_price = cost_price,
                sell_price = sell_price,
                total      = qty * cost_price,
            )
            total += qty * cost_price

        purchase.total_amount = total
        purchase.debt_amount  = total
        purchase.paid_amount  = Decimal("0")
        purchase.save(update_fields=["total_amount", "debt_amount", "paid_amount"])

        return purchase

    # ── Receive ───────────────────────────────────────────────────────────

    @staticmethod
    @transaction.atomic
    def receive(purchase: Purchase, created_by=None) -> Purchase:
        """
        Xaridni qabul qilish:
          - Har bir item ombor ga tushadi (StockService.add)
          - Product.cost_price va sell_price yangilanadi
          - Status = received
        """
        if purchase.status != PurchaseStatus.DRAFT:
            raise BusinessLogicError(
                "Faqat 'Qoralama' holatdagi xarid qabul qilinadi.",
                "invalid_status",
            )

        items = purchase.items.select_related("product").filter(deleted_at__isnull=True)

        for item in items:
            # 1. Omborga qo'shish
            StockService.add(
                product     = item.product,
                quantity    = item.quantity,
                source_type = "purchase",
                source_id   = purchase.pk,
                reason      = f"Xarid #{purchase.pk} qabul qilindi",
                created_by  = created_by,
            )
            # 2. Product narxini yangilash
            item.product.cost_price = item.cost_price
            item.product.sell_price = item.sell_price
            item.product.save(update_fields=["cost_price", "sell_price", "updated_at"])

        purchase.status      = PurchaseStatus.RECEIVED
        purchase.received_at = timezone.now()
        purchase.save(update_fields=["status", "received_at"])

        return purchase

    # ── Pay ───────────────────────────────────────────────────────────────

    @staticmethod
    @transaction.atomic
    def pay(
        purchase: Purchase,
        amount: Decimal,
        note: str = "",
        paid_by=None,
    ) -> PurchasePayment:
        """
        Qarz to'lash — qisman yoki to'liq.
        """
        if purchase.status == PurchaseStatus.DRAFT:
            raise BusinessLogicError(
                "Qoralama xaridga to'lov qilish mumkin emas.",
                "invalid_status",
            )
        if purchase.status == PurchaseStatus.PAID:
            raise BusinessLogicError("Xarid allaqachon to'liq to'langan.", "already_paid")
        if purchase.status == PurchaseStatus.CANCELLED:
            raise BusinessLogicError("Bekor qilingan xaridga to'lov qilish mumkin emas.", "cancelled")
        if amount <= 0:
            raise BusinessLogicError("To'lov summasi musbat bo'lishi kerak.", "invalid_amount")
        if amount > purchase.debt_amount:
            raise BusinessLogicError(
                f"To'lov summasi qarzdan ({purchase.debt_amount}) ko'p bo'lishi mumkin emas.",
                "overpayment",
            )

        payment = PurchasePayment.objects.create(
            purchase = purchase,
            amount   = amount,
            note     = note,
            paid_by  = paid_by,
        )

        purchase.paid_amount += amount
        purchase.debt_amount -= amount
        purchase.status = (
            PurchaseStatus.PAID if purchase.debt_amount <= 0
            else PurchaseStatus.PARTIAL
        )
        purchase.save(update_fields=["paid_amount", "debt_amount", "status"])

        return payment

    # ── Cancel ────────────────────────────────────────────────────────────

    @staticmethod
    @transaction.atomic
    def cancel(purchase: Purchase, reason: str = "", created_by=None) -> Purchase:
        """
        Xaridni bekor qilish.
        Agar received bo'lgan bo'lsa — ombordan chiqarib olinadi.
        """
        if purchase.status in (PurchaseStatus.PAID, PurchaseStatus.PARTIAL):
            raise BusinessLogicError(
                "To'lov qilingan xaridni bekor qilish mumkin emas.",
                "cannot_cancel",
            )
        if purchase.status == PurchaseStatus.CANCELLED:
            raise BusinessLogicError("Xarid allaqachon bekor qilingan.", "already_cancelled")

        if purchase.status == PurchaseStatus.RECEIVED:
            # Ombordan chiqarib olamiz.
            # Edge case: agar mahsulotlar sotilib ketgan bo'lsa (stock < item.qty),
            # xatoga yo'l qo'ymaslik uchun mavjud miqdorni 0 ga tushuramiz.
            import logging
            logger = logging.getLogger(__name__)

            from inventory.models import Stock
            from decimal import Decimal

            items = purchase.items.select_related("product").filter(deleted_at__isnull=True)
            for item in items:
                try:
                    stock     = Stock.objects.select_for_update().get(product=item.product)
                    qty_to_deduct = min(item.quantity, stock.quantity)

                    if qty_to_deduct < item.quantity:
                        logger.warning(
                            "purchase.cancel #%s: %s mahsulotdan %s dona so'raldi, "
                            "lekin omborda faqat %s dona bor — mavjud miqdor chiqarildi.",
                            purchase.pk, item.product.name,
                            item.quantity, stock.quantity,
                        )

                    if qty_to_deduct > Decimal("0"):
                        StockService.deduct(
                            product     = item.product,
                            quantity    = qty_to_deduct,
                            source_type = "purchase_cancel",
                            source_id   = purchase.pk,
                            reason      = f"Xarid #{purchase.pk} bekor qilindi: {reason}",
                            created_by  = created_by,
                        )
                except Stock.DoesNotExist:
                    logger.warning(
                        "purchase.cancel #%s: %s mahsulot uchun stock topilmadi — o'tkazib yuborildi.",
                        purchase.pk, item.product.name,
                    )

        purchase.status = PurchaseStatus.CANCELLED
        if reason:
            purchase.note = f"{purchase.note}\n[Bekor: {reason}]".strip()
        purchase.save(update_fields=["status", "note"])
        return purchase

    # ── Query helpers ─────────────────────────────────────────────────────

    @staticmethod
    def get_queryset():
        return (
            Purchase.objects
            .filter(deleted_at__isnull=True)
            .select_related("company", "branch", "created_by")
            .prefetch_related("items__product", "payments")
            .order_by("-created_at")
        )

    @staticmethod
    def get_debts():
        """Hali to'lanmagan xaridlar."""
        from purchases.models import PurchaseStatus as PS
        return (
            Purchase.objects
            .filter(
                deleted_at__isnull=True,
                status__in=[PS.RECEIVED, PS.PARTIAL],
                debt_amount__gt=0,
            )
            .select_related("company", "branch")
            .order_by("due_date")
        )

    @staticmethod
    def get_overdue():
        """Muddati o'tgan qarzlar — bugun va undan oldingi muddatlar."""
        from datetime import date as date_cls
        today = date_cls.today()
        return PurchaseService.get_debts().filter(
            due_date__isnull=False,
            due_date__lt=today,
        )
