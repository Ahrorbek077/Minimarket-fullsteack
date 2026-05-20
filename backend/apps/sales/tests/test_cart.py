"""
CartService testlari — Redis cart.
pytest -v sales/tests/test_cart.py
"""
import pytest
from decimal import Decimal
from unittest.mock import patch

from core.exceptions import BusinessLogicError, InsufficientStockError
from sales.cart import CartService


@pytest.fixture(autouse=True)
def clear_cache():
    """Har test dan keyin cache tozalanadi."""
    from django.core.cache import cache
    yield
    cache.clear()


USER_ID = 1


@pytest.mark.django_db
class TestCartAdd:

    def test_add_item(self):
        from products.tests.factories import ProductFactory
        from inventory.tests.factories import StockFactory
        product = ProductFactory(sell_price=Decimal("5000"))
        StockFactory(product=product, quantity=Decimal("100"))

        cart = CartService.add_item(USER_ID, product.pk, Decimal("3"))
        assert cart["item_count"] == 1
        assert Decimal(cart["total_amount"]) == Decimal("15000")

    def test_add_same_product_twice_accumulates(self):
        from products.tests.factories import ProductFactory
        from inventory.tests.factories import StockFactory
        product = ProductFactory(sell_price=Decimal("2000"))
        StockFactory(product=product, quantity=Decimal("50"))

        CartService.add_item(USER_ID, product.pk, Decimal("2"))
        cart = CartService.add_item(USER_ID, product.pk, Decimal("3"))

        assert cart["item_count"] == 1
        assert cart["items"][0]["quantity"] == "5.00"
        assert Decimal(cart["total_amount"]) == Decimal("10000")

    def test_add_multiple_products(self):
        from products.tests.factories import ProductFactory
        from inventory.tests.factories import StockFactory
        p1 = ProductFactory(sell_price=Decimal("3000"))
        p2 = ProductFactory(sell_price=Decimal("7000"))
        StockFactory(product=p1, quantity=Decimal("10"))
        StockFactory(product=p2, quantity=Decimal("10"))

        CartService.add_item(USER_ID, p1.pk, Decimal("2"))
        cart = CartService.add_item(USER_ID, p2.pk, Decimal("1"))

        assert cart["item_count"] == 2
        assert Decimal(cart["total_amount"]) == Decimal("13000")

    def test_add_exceeds_stock_raises(self):
        from products.tests.factories import ProductFactory
        from inventory.tests.factories import StockFactory
        product = ProductFactory()
        StockFactory(product=product, quantity=Decimal("5"))

        with pytest.raises(InsufficientStockError):
            CartService.add_item(USER_ID, product.pk, Decimal("10"))

    def test_add_zero_quantity_raises(self):
        from products.tests.factories import ProductFactory
        product = ProductFactory()
        with pytest.raises(BusinessLogicError, match="musbat"):
            CartService.add_item(USER_ID, product.pk, Decimal("0"))

    def test_add_inactive_product_raises(self):
        from products.tests.factories import ProductFactory
        product = ProductFactory(is_active=False)
        with pytest.raises(BusinessLogicError, match="topilmadi"):
            CartService.add_item(USER_ID, product.pk, Decimal("1"))

    def test_add_nonexistent_product_raises(self):
        with pytest.raises(BusinessLogicError):
            CartService.add_item(USER_ID, 99999, Decimal("1"))


@pytest.mark.django_db
class TestCartScan:

    def test_scan_by_barcode(self):
        from products.tests.factories import ProductFactory
        from inventory.tests.factories import StockFactory
        product = ProductFactory(barcode="1234567890001", sell_price=Decimal("4000"))
        StockFactory(product=product, quantity=Decimal("20"))

        cart = CartService.add_by_barcode(USER_ID, "1234567890001", Decimal("2"))
        assert cart["item_count"] == 1
        assert Decimal(cart["total_amount"]) == Decimal("8000")

    def test_scan_invalid_barcode_raises(self):
        from core.exceptions import BusinessLogicError
        with pytest.raises(BusinessLogicError):
            CartService.add_by_barcode(USER_ID, "9999999999999")


@pytest.mark.django_db
class TestCartUpdate:

    def test_update_quantity(self):
        from products.tests.factories import ProductFactory
        from inventory.tests.factories import StockFactory
        product = ProductFactory(sell_price=Decimal("3000"))
        StockFactory(product=product, quantity=Decimal("50"))
        CartService.add_item(USER_ID, product.pk, Decimal("5"))

        cart = CartService.update_item(USER_ID, product.pk, Decimal("2"))
        assert cart["items"][0]["quantity"] == "2.00"
        assert Decimal(cart["total_amount"]) == Decimal("6000")

    def test_update_to_zero_removes_item(self):
        from products.tests.factories import ProductFactory
        from inventory.tests.factories import StockFactory
        product = ProductFactory()
        StockFactory(product=product, quantity=Decimal("10"))
        CartService.add_item(USER_ID, product.pk, Decimal("3"))

        cart = CartService.update_item(USER_ID, product.pk, Decimal("0"))
        assert cart["item_count"] == 0

    def test_update_nonexistent_raises(self):
        with pytest.raises(BusinessLogicError, match="cartda yo'q"):
            CartService.update_item(USER_ID, 99999, Decimal("1"))


@pytest.mark.django_db
class TestCartRemoveAndClear:

    def test_remove_item(self):
        from products.tests.factories import ProductFactory
        from inventory.tests.factories import StockFactory
        p1 = ProductFactory()
        p2 = ProductFactory()
        StockFactory(product=p1, quantity=Decimal("10"))
        StockFactory(product=p2, quantity=Decimal("10"))
        CartService.add_item(USER_ID, p1.pk, Decimal("1"))
        CartService.add_item(USER_ID, p2.pk, Decimal("1"))

        cart = CartService.remove_item(USER_ID, p1.pk)
        assert cart["item_count"] == 1
        assert cart["items"][0]["product_id"] == p2.pk

    def test_remove_nonexistent_raises(self):
        with pytest.raises(BusinessLogicError, match="cartda yo'q"):
            CartService.remove_item(USER_ID, 99999)

    def test_clear_cart(self):
        from products.tests.factories import ProductFactory
        from inventory.tests.factories import StockFactory
        product = ProductFactory()
        StockFactory(product=product, quantity=Decimal("10"))
        CartService.add_item(USER_ID, product.pk, Decimal("2"))

        CartService.clear(USER_ID)
        cart = CartService.get_cart(USER_ID)
        assert cart["item_count"] == 0
        assert Decimal(cart["total_amount"]) == Decimal("0")

    def test_different_users_separate_carts(self):
        from products.tests.factories import ProductFactory
        from inventory.tests.factories import StockFactory
        product = ProductFactory()
        StockFactory(product=product, quantity=Decimal("50"))

        CartService.add_item(1, product.pk, Decimal("3"))
        CartService.add_item(2, product.pk, Decimal("7"))

        cart1 = CartService.get_cart(1)
        cart2 = CartService.get_cart(2)
        assert cart1["items"][0]["quantity"] == "3.00"
        assert cart2["items"][0]["quantity"] == "7.00"
