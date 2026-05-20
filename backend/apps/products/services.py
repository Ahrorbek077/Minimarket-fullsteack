"""
Products services — barcha biznes logika shu yerda.
"""
from django.db import transaction

from core.exceptions import BusinessLogicError
from .models import Category, Product, Unit


class CategoryService:

    @staticmethod
    def create(name: str, parent_id: int = None, **kwargs) -> Category:
        if parent_id:
            parent = Category.objects.filter(
                pk=parent_id, deleted_at__isnull=True
            ).first()
            if not parent:
                raise BusinessLogicError("Ota kategoriya topilmadi.", "not_found")
        return Category.objects.create(name=name, parent_id=parent_id, **kwargs)

    @staticmethod
    def get_tree() -> list:
        """Faqat root kategoriyalar + children prefetch."""
        return (
            Category.objects
            .filter(parent__isnull=True, deleted_at__isnull=True)
            .prefetch_related("children")
            .order_by("order", "name")
        )


class UnitService:

    @staticmethod
    def get_all():
        return Unit.objects.filter(deleted_at__isnull=True).order_by("name")


class ProductService:

    @staticmethod
    def get_queryset():
        """Asosiy queryset — optimized."""
        return (
            Product.objects
            .filter(deleted_at__isnull=True)
            .select_related("category", "unit")
            .order_by("name")
        )

    @staticmethod
    def get_active():
        return ProductService.get_queryset().filter(is_active=True)

    @staticmethod
    def get_by_barcode(barcode: str) -> Product:
        """Barcode yoki QR kod orqali mahsulot topish."""
        product = (
            Product.objects
            .select_related("category", "unit")
            .filter(
                barcode=barcode,
                deleted_at__isnull=True,
                is_active=True,
            )
            .first()
        )
        if not product:
            raise BusinessLogicError(
                f"'{barcode}' barcodeli mahsulot topilmadi.",
                "product_not_found",
            )
        return product

    @staticmethod
    @transaction.atomic
    def create(validated_data: dict) -> Product:
        return Product.objects.create(**validated_data)

    @staticmethod
    @transaction.atomic
    def update(product: Product, validated_data: dict) -> Product:
        for field, value in validated_data.items():
            setattr(product, field, value)
        product.save()
        return product

    @staticmethod
    def update_prices(product: Product, cost_price=None, sell_price=None) -> Product:
        """Narxlarni yangilash."""
        from decimal import Decimal
        if cost_price is not None:
            product.cost_price = Decimal(str(cost_price))
        if sell_price is not None:
            product.sell_price = Decimal(str(sell_price))
        product.save(update_fields=["cost_price", "sell_price", "updated_at"])
        return product

    @staticmethod
    def get_low_stock_products():
        """Minimum qoldiqdan past mahsulotlar."""
        from django.db.models import F
        return (
            ProductService.get_active()
            .select_related("stock")
            .filter(stock__quantity__lte=F("min_stock"))
        )
