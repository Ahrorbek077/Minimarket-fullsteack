"""
Inventory model testlari.
pytest -v inventory/tests/test_models.py
"""
import pytest
from decimal import Decimal
from products.tests.factories import ProductFactory
from inventory.models import Stock, StockMovement, MovementType
from .factories import StockFactory, StockMovementFactory


@pytest.mark.django_db
class TestStockModel:

    def test_stock_created_with_product(self):
        """Product yaratilganda Stock avtomatik yaratiladi (signal)."""
        product = ProductFactory()
        assert Stock.objects.filter(product=product).exists()
        assert product.stock.quantity == Decimal("0")

    def test_is_low_true(self):
        product = ProductFactory(min_stock=Decimal("10"))
        stock   = StockFactory(product=product, quantity=Decimal("5"))
        assert stock.is_low is True

    def test_is_low_false(self):
        product = ProductFactory(min_stock=Decimal("5"))
        stock   = StockFactory(product=product, quantity=Decimal("10"))
        assert stock.is_low is False

    def test_is_low_equal_min(self):
        """Min ga teng bo'lsa ham low hisoblanadi."""
        product = ProductFactory(min_stock=Decimal("10"))
        stock   = StockFactory(product=product, quantity=Decimal("10"))
        assert stock.is_low is True

    def test_is_empty_true(self):
        product = ProductFactory()
        stock   = StockFactory(product=product, quantity=Decimal("0"))
        assert stock.is_empty is True

    def test_is_empty_false(self):
        product = ProductFactory()
        stock   = StockFactory(product=product, quantity=Decimal("1"))
        assert stock.is_empty is False

    def test_str(self):
        from products.tests.factories import UnitFactory
        unit    = UnitFactory(short_name="kg")
        product = ProductFactory(name="Un", unit=unit)
        stock   = StockFactory(product=product, quantity=Decimal("50"))
        assert "Un" in str(stock)
        assert "50" in str(stock)


@pytest.mark.django_db
class TestStockMovementModel:

    def test_create_movement(self):
        mv = StockMovementFactory(
            movement_type=MovementType.IN,
            quantity=Decimal("20"),
        )
        assert mv.pk is not None
        assert mv.movement_type == MovementType.IN

    def test_str_contains_type_and_product(self):
        product = ProductFactory(name="Guruch")
        mv = StockMovementFactory(
            product=product,
            movement_type=MovementType.OUT,
            quantity=Decimal("5"),
        )
        result = str(mv)
        assert "Chiqdi" in result
        assert "Guruch" in result
