"""
Inventory services — barcha stock operatsiyalari shu yerda.

Qoida:
  - Stock.quantity ni to'g'ridan-to'g'ri o'zgartirmang.
  - Faqat StockService metodlarini ishlating.
  - Har bir o'zgarish StockMovement ga yoziladi.
"""
from decimal import Decimal

from django.db import transaction
from django.db.models import F, Sum, Q

from core.exceptions import BusinessLogicError, InsufficientStockError
from .models import MovementType, Stock, StockMovement


class StockService:
    """
    Ombor operatsiyalari.
    Barcha metod @transaction.atomic — xato bo'lsa rollback.
    """

    # ── Internal helper ───────────────────────────────────────────────────

    @staticmethod
    def _get_or_create_stock(product) -> Stock:
        stock, _ = Stock.objects.select_for_update().get_or_create(
            product=product,
            defaults={"quantity": Decimal("0")},
        )
        return stock

    @staticmethod
    def _write_movement(
        product,
        movement_type: str,
        quantity: Decimal,
        qty_before: Decimal,
        qty_after: Decimal,
        source_type: str = "",
        source_id: int = None,
        reason: str = "",
        created_by=None,
    ) -> StockMovement:
        return StockMovement.objects.create(
            product=product,
            movement_type=movement_type,
            quantity=quantity,
            qty_before=qty_before,
            qty_after=qty_after,
            source_type=source_type,
            source_id=source_id,
            reason=reason,
            created_by=created_by,
        )

    # ── Public API ────────────────────────────────────────────────────────

    @staticmethod
    @transaction.atomic
    def add(
        product,
        quantity: Decimal,
        source_type: str = "manual",
        source_id: int = None,
        reason: str = "",
        created_by=None,
    ) -> StockMovement:
        """
        Omborga mahsulot qo'shish (xarid / qabul).
        Purchase signali ham shu metodga murojaat qiladi.
        """
        if quantity <= 0:
            raise BusinessLogicError("Miqdor musbat bo'lishi kerak.", "invalid_quantity")

        stock       = StockService._get_or_create_stock(product)
        qty_before  = stock.quantity
        stock.quantity = F("quantity") + quantity
        stock.save(update_fields=["quantity", "updated_at"])
        stock.refresh_from_db()

        return StockService._write_movement(
            product=product,
            movement_type=MovementType.IN,
            quantity=quantity,
            qty_before=qty_before,
            qty_after=stock.quantity,
            source_type=source_type,
            source_id=source_id,
            reason=reason,
            created_by=created_by,
        )

    @staticmethod
    @transaction.atomic
    def deduct(
        product,
        quantity: Decimal,
        source_type: str = "manual",
        source_id: int = None,
        reason: str = "",
        created_by=None,
    ) -> StockMovement:
        """
        Ombordan mahsulot chiqarish (sotuv).
        Sale signali shu metodga murojaat qiladi.
        Yetarli qoldiq bo'lmasa InsufficientStockError.
        """
        if quantity <= 0:
            raise BusinessLogicError("Miqdor musbat bo'lishi kerak.", "invalid_quantity")

        stock = StockService._get_or_create_stock(product)

        if stock.quantity < quantity:
            raise InsufficientStockError(
                f"'{product.name}' dan yetarli qoldiq yo'q. "
                f"Mavjud: {stock.quantity}, kerak: {quantity}."
            )

        qty_before     = stock.quantity
        stock.quantity = F("quantity") - quantity
        stock.save(update_fields=["quantity", "updated_at"])
        stock.refresh_from_db()

        return StockService._write_movement(
            product=product,
            movement_type=MovementType.OUT,
            quantity=quantity,
            qty_before=qty_before,
            qty_after=stock.quantity,
            source_type=source_type,
            source_id=source_id,
            reason=reason,
            created_by=created_by,
        )

    @staticmethod
    @transaction.atomic
    def return_to_stock(
        product,
        quantity: Decimal,
        source_type: str = "sale",
        source_id: int = None,
        reason: str = "Qaytarish",
        created_by=None,
    ) -> StockMovement:
        """
        Sotilgan mahsulot qaytib kelganda omborga qo'shish.
        """
        if quantity <= 0:
            raise BusinessLogicError("Miqdor musbat bo'lishi kerak.", "invalid_quantity")

        stock      = StockService._get_or_create_stock(product)
        qty_before = stock.quantity
        stock.quantity = F("quantity") + quantity
        stock.save(update_fields=["quantity", "updated_at"])
        stock.refresh_from_db()

        return StockService._write_movement(
            product=product,
            movement_type=MovementType.RETURN_IN,
            quantity=quantity,
            qty_before=qty_before,
            qty_after=stock.quantity,
            source_type=source_type,
            source_id=source_id,
            reason=reason,
            created_by=created_by,
        )

    @staticmethod
    @transaction.atomic
    def adjust(
        product,
        new_quantity: Decimal,
        reason: str = "",
        created_by=None,
    ) -> StockMovement:
        """
        Manual tuzatish — haqiqiy sanash natijasi bilan moslashtirish.
        new_quantity — bo'lishi kerak bo'lgan miqdor.
        """
        if new_quantity < 0:
            raise BusinessLogicError("Miqdor manfiy bo'lishi mumkin emas.", "invalid_quantity")

        stock      = StockService._get_or_create_stock(product)
        qty_before = stock.quantity
        diff       = new_quantity - qty_before

        stock.quantity = new_quantity
        stock.save(update_fields=["quantity", "updated_at"])

        return StockService._write_movement(
            product=product,
            movement_type=MovementType.ADJUST,
            quantity=abs(diff),
            qty_before=qty_before,
            qty_after=new_quantity,
            source_type="manual",
            reason=reason or f"Tuzatish: {qty_before} → {new_quantity}",
            created_by=created_by,
        )

    # ── Query helpers ─────────────────────────────────────────────────────

    @staticmethod
    def get_current_quantity(product) -> Decimal:
        try:
            # Cache bo'lmasligi uchun DB dan o'qiymiz
            stock = Stock.objects.get(product=product)
            return stock.quantity
        except Stock.DoesNotExist:
            return Decimal("0")

    @staticmethod
    def get_low_stock():
        """Min qoldiqdan past yoki teng bo'lgan stocklar."""
        return (
            Stock.objects
            .select_related("product", "product__unit", "product__category")
            .filter(
                product__deleted_at__isnull=True,
                product__is_active=True,
                quantity__lte=F("product__min_stock"),
            )
            .order_by("quantity")
        )

    @staticmethod
    def get_movements(product=None, movement_type=None, source_type=None):
        """Filtrlangan harakat tarixi."""
        qs = (
            StockMovement.objects
            .select_related("product", "product__unit", "created_by")
            .filter(deleted_at__isnull=True)
        )
        if product:
            qs = qs.filter(product=product)
        if movement_type:
            qs = qs.filter(movement_type=movement_type)
        if source_type:
            qs = qs.filter(source_type=source_type)
        return qs.order_by("-created_at")

    @staticmethod
    def get_stock_summary():
        """
        Dashboard uchun — jami stock statistikasi.
        """
        from products.models import Product
        total_products = Product.objects.filter(
            deleted_at__isnull=True, is_active=True
        ).count()
        low_stock_count = StockService.get_low_stock().count()
        out_of_stock    = Stock.objects.filter(quantity__lte=0).count()

        total_value = (
            Stock.objects
            .filter(product__deleted_at__isnull=True)
            .aggregate(
                cost_value=Sum(F("quantity") * F("product__cost_price")),
                sell_value=Sum(F("quantity") * F("product__sell_price")),
            )
        )

        return {
            "total_products":   total_products,
            "low_stock_count":  low_stock_count,
            "out_of_stock":     out_of_stock,
            "total_cost_value": total_value["cost_value"] or 0,
            "total_sell_value": total_value["sell_value"] or 0,
        }
