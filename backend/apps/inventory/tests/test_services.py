"""
StockService testlari — barcha ombor operatsiyalari.
pytest -v inventory/tests/test_services.py
"""
import pytest
from decimal import Decimal

from core.exceptions import BusinessLogicError, InsufficientStockError
from inventory.models import MovementType, Stock, StockMovement
from inventory.services import StockService
from products.tests.factories import ProductFactory
from users.tests.factories import UserFactory
from .factories import StockFactory


@pytest.mark.django_db
class TestStockServiceAdd:

    def test_add_creates_movement(self):
        product  = ProductFactory()
        movement = StockService.add(product, Decimal("50"))
        assert movement.movement_type == MovementType.IN
        assert movement.quantity      == Decimal("50")
        assert movement.qty_before    == Decimal("0")
        assert movement.qty_after     == Decimal("50")

    def test_add_increases_stock(self):
        product = ProductFactory()
        StockService.add(product, Decimal("30"))
        StockService.add(product, Decimal("20"))
        product.stock.refresh_from_db()
        assert product.stock.quantity == Decimal("50")

    def test_add_zero_raises(self):
        product = ProductFactory()
        with pytest.raises(BusinessLogicError, match="musbat"):
            StockService.add(product, Decimal("0"))

    def test_add_negative_raises(self):
        product = ProductFactory()
        with pytest.raises(BusinessLogicError):
            StockService.add(product, Decimal("-10"))

    def test_add_records_source(self):
        product  = ProductFactory()
        movement = StockService.add(
            product, Decimal("10"),
            source_type="purchase", source_id=42
        )
        assert movement.source_type == "purchase"
        assert movement.source_id   == 42

    def test_add_records_created_by(self):
        product = ProductFactory()
        user    = UserFactory()
        mv      = StockService.add(product, Decimal("5"), created_by=user)
        assert mv.created_by == user


@pytest.mark.django_db
class TestStockServiceDeduct:

    def test_deduct_success(self):
        product = ProductFactory()
        StockFactory(product=product, quantity=Decimal("100"))
        movement = StockService.deduct(product, Decimal("30"))
        assert movement.movement_type == MovementType.OUT
        assert movement.qty_before    == Decimal("100")
        assert movement.qty_after     == Decimal("70")
        product.stock.refresh_from_db()
        assert product.stock.quantity == Decimal("70")

    def test_deduct_exact_quantity_ok(self):
        """Aniq qoldiqcha chiqarish — muvaffaqiyatli."""
        product = ProductFactory()
        StockFactory(product=product, quantity=Decimal("10"))
        StockService.deduct(product, Decimal("10"))
        product.stock.refresh_from_db()
        assert product.stock.quantity == Decimal("0")

    def test_deduct_insufficient_raises(self):
        product = ProductFactory()
        StockFactory(product=product, quantity=Decimal("5"))
        with pytest.raises(InsufficientStockError) as exc:
            StockService.deduct(product, Decimal("10"))
        assert "yetarli qoldiq yo'q" in str(exc.value.detail)

    def test_deduct_empty_stock_raises(self):
        product = ProductFactory()
        # Stock = 0 (signal orqali yaratilgan)
        with pytest.raises(InsufficientStockError):
            StockService.deduct(product, Decimal("1"))

    def test_deduct_zero_raises(self):
        product = ProductFactory()
        StockFactory(product=product, quantity=Decimal("10"))
        with pytest.raises(BusinessLogicError):
            StockService.deduct(product, Decimal("0"))


@pytest.mark.django_db
class TestStockServiceReturn:

    def test_return_to_stock(self):
        product = ProductFactory()
        StockFactory(product=product, quantity=Decimal("50"))
        mv = StockService.return_to_stock(product, Decimal("5"))
        assert mv.movement_type == MovementType.RETURN_IN
        product.stock.refresh_from_db()
        assert product.stock.quantity == Decimal("55")

    def test_return_zero_raises(self):
        product = ProductFactory()
        with pytest.raises(BusinessLogicError):
            StockService.return_to_stock(product, Decimal("0"))


@pytest.mark.django_db
class TestStockServiceAdjust:

    def test_adjust_up(self):
        product = ProductFactory()
        StockFactory(product=product, quantity=Decimal("10"))
        mv = StockService.adjust(product, Decimal("25"), reason="Haqiqiy sanoq")
        assert mv.movement_type == MovementType.ADJUST
        assert mv.qty_before    == Decimal("10")
        assert mv.qty_after     == Decimal("25")
        assert mv.quantity      == Decimal("15")  # diff
        product.stock.refresh_from_db()
        assert product.stock.quantity == Decimal("25")

    def test_adjust_down(self):
        product = ProductFactory()
        StockFactory(product=product, quantity=Decimal("50"))
        mv = StockService.adjust(product, Decimal("30"))
        assert mv.quantity   == Decimal("20")  # abs diff
        assert mv.qty_after  == Decimal("30")

    def test_adjust_to_zero(self):
        product = ProductFactory()
        StockFactory(product=product, quantity=Decimal("10"))
        mv = StockService.adjust(product, Decimal("0"))
        product.stock.refresh_from_db()
        assert product.stock.quantity == Decimal("0")

    def test_adjust_negative_raises(self):
        product = ProductFactory()
        with pytest.raises(BusinessLogicError, match="manfiy"):
            StockService.adjust(product, Decimal("-5"))


@pytest.mark.django_db
class TestStockServiceHelpers:

    def test_get_current_quantity(self):
        product = ProductFactory()
        StockFactory(product=product, quantity=Decimal("77"))
        assert StockService.get_current_quantity(product) == Decimal("77")

    def test_get_current_quantity_no_stock(self):
        """Stock bo'lmasa 0 qaytaradi."""
        from products.models import Product
        # Stock o'chirilgan product simulyatsiya
        product = ProductFactory()
        # Stock ni o'chirib tashlaymiz
        product.stock.delete()
        qty = StockService.get_current_quantity(product)
        assert qty == Decimal("0")

    def test_get_low_stock(self):
        low_product  = ProductFactory(min_stock=Decimal("20"))
        ok_product   = ProductFactory(min_stock=Decimal("5"))
        StockFactory(product=low_product, quantity=Decimal("5"))   # low!
        StockFactory(product=ok_product,  quantity=Decimal("50"))  # ok
        low_stocks = list(StockService.get_low_stock())
        products   = [s.product for s in low_stocks]
        assert low_product in products
        assert ok_product  not in products

    def test_get_stock_summary(self):
        ProductFactory.create_batch(3)
        summary = StockService.get_stock_summary()
        assert "total_products"   in summary
        assert "low_stock_count"  in summary
        assert "out_of_stock"     in summary
        assert "total_cost_value" in summary
        assert "total_sell_value" in summary

    def test_atomic_deduct_rollback(self):
        """
        Tranzaksiya ichida xato bo'lsa qoldiq o'zgarmasligi kerak.
        """
        from django.db import transaction
        product = ProductFactory()
        StockFactory(product=product, quantity=Decimal("20"))

        try:
            with transaction.atomic():
                StockService.deduct(product, Decimal("5"))
                raise ValueError("Simulyatsiya xatosi")
        except ValueError:
            pass

        product.stock.refresh_from_db()
        assert product.stock.quantity == Decimal("20")  # rollback ishladi
