"""
SaleService testlari — checkout, return.
pytest -v sales/tests/test_services.py
"""
import pytest
from decimal import Decimal

from core.exceptions import BusinessLogicError
from inventory.models import MovementType, StockMovement
from inventory.tests.factories import StockFactory
from products.tests.factories import ProductFactory
from users.tests.factories import UserFactory
from sales.cart import CartService
from sales.models import PaymentMethod, SaleStatus
from sales.services import SaleService


@pytest.fixture(autouse=True)
def clear_cache():
    from django.core.cache import cache
    yield
    cache.clear()


def fill_cart(user_id, items):
    """Helper: [(product, qty)] → cart."""
    for product, qty in items:
        CartService.add_item(user_id, product.pk, qty)


@pytest.mark.django_db
class TestCheckout:

    def test_checkout_cash(self):
        user    = UserFactory()
        product = ProductFactory(sell_price=Decimal("10000"), cost_price=Decimal("7000"))
        StockFactory(product=product, quantity=Decimal("20"))
        fill_cart(user.pk, [(product, Decimal("3"))])

        sale = SaleService.checkout(
            user_id  = user.pk,
            payments = [{"method": PaymentMethod.CASH, "amount": "30000"}],
            cashier  = user,
        )
        assert sale.status       == SaleStatus.COMPLETED
        assert sale.net_amount   == Decimal("30000")
        assert sale.paid_amount  == Decimal("30000")
        assert sale.debt_amount  == Decimal("0")
        assert sale.items.count()    == 1
        assert sale.payments.count() == 1

    def test_checkout_deducts_stock(self):
        user    = UserFactory()
        product = ProductFactory(sell_price=Decimal("5000"))
        StockFactory(product=product, quantity=Decimal("10"))
        fill_cart(user.pk, [(product, Decimal("4"))])

        SaleService.checkout(
            user_id  = user.pk,
            payments = [{"method": PaymentMethod.CASH, "amount": "20000"}],
            cashier  = user,
        )
        product.stock.refresh_from_db()
        assert product.stock.quantity == Decimal("6")

    def test_checkout_creates_stock_movement(self):
        user    = UserFactory()
        product = ProductFactory(sell_price=Decimal("3000"))
        StockFactory(product=product, quantity=Decimal("10"))
        fill_cart(user.pk, [(product, Decimal("2"))])

        sale = SaleService.checkout(
            user_id  = user.pk,
            payments = [{"method": PaymentMethod.CASH, "amount": "6000"}],
            cashier  = user,
        )
        mv = StockMovement.objects.filter(
            product=product, movement_type=MovementType.OUT,
            source_type="sale", source_id=sale.pk,
        ).first()
        assert mv is not None
        assert mv.quantity == Decimal("2")

    def test_checkout_mixed_payment(self):
        """Naqd + karta + nasiya."""
        user    = UserFactory()
        product = ProductFactory(sell_price=Decimal("10000"))
        StockFactory(product=product, quantity=Decimal("5"))
        fill_cart(user.pk, [(product, Decimal("3"))])

        sale = SaleService.checkout(
            user_id  = user.pk,
            payments = [
                {"method": PaymentMethod.CASH, "amount": "10000"},
                {"method": PaymentMethod.CARD, "amount": "10000"},
                {"method": PaymentMethod.DEBT, "amount": "10000"},
            ],
            cashier  = user,
        )
        assert sale.debt_amount  == Decimal("10000")
        assert sale.paid_amount  == Decimal("20000")
        assert sale.payments.count() == 3

    def test_checkout_with_discount(self):
        user    = UserFactory()
        product = ProductFactory(sell_price=Decimal("10000"))
        StockFactory(product=product, quantity=Decimal("10"))
        fill_cart(user.pk, [(product, Decimal("2"))])

        sale = SaleService.checkout(
            user_id      = user.pk,
            payments     = [{"method": PaymentMethod.CASH, "amount": "18000"}],
            discount_pct = Decimal("10"),
            cashier      = user,
        )
        assert sale.total_amount    == Decimal("20000")
        assert sale.discount_amount == Decimal("2000")
        assert sale.net_amount      == Decimal("18000")

    def test_checkout_clears_cart(self):
        user    = UserFactory()
        product = ProductFactory(sell_price=Decimal("5000"))
        StockFactory(product=product, quantity=Decimal("10"))
        fill_cart(user.pk, [(product, Decimal("1"))])

        SaleService.checkout(
            user_id  = user.pk,
            payments = [{"method": PaymentMethod.CASH, "amount": "5000"}],
            cashier  = user,
        )
        cart = CartService.get_cart(user.pk)
        assert cart["item_count"] == 0

    def test_checkout_empty_cart_raises(self):
        user = UserFactory()
        with pytest.raises(BusinessLogicError, match="bo'sh"):
            SaleService.checkout(
                user_id  = user.pk,
                payments = [{"method": PaymentMethod.CASH, "amount": "1000"}],
            )

    def test_checkout_insufficient_payment_raises(self):
        user    = UserFactory()
        product = ProductFactory(sell_price=Decimal("10000"))
        StockFactory(product=product, quantity=Decimal("5"))
        fill_cart(user.pk, [(product, Decimal("1"))])

        with pytest.raises(BusinessLogicError, match="yetarli emas"):
            SaleService.checkout(
                user_id  = user.pk,
                payments = [{"method": PaymentMethod.CASH, "amount": "5000"}],
            )

    def test_checkout_generates_unique_invoice_no(self):
        user = UserFactory()
        for _ in range(3):
            product = ProductFactory(sell_price=Decimal("1000"))
            StockFactory(product=product, quantity=Decimal("10"))
            fill_cart(user.pk, [(product, Decimal("1"))])
            SaleService.checkout(
                user_id  = user.pk,
                payments = [{"method": PaymentMethod.CASH, "amount": "1000"}],
                cashier  = user,
            )
            CartService.clear(user.pk)

        from sales.models import Sale
        invoice_nos = list(Sale.objects.values_list("invoice_no", flat=True))
        assert len(invoice_nos) == len(set(invoice_nos))


@pytest.mark.django_db
class TestReturnSale:

    def _make_sale(self):
        user    = UserFactory()
        product = ProductFactory(sell_price=Decimal("5000"))
        StockFactory(product=product, quantity=Decimal("10"))
        fill_cart(user.pk, [(product, Decimal("4"))])
        sale = SaleService.checkout(
            user_id  = user.pk,
            payments = [{"method": PaymentMethod.CASH, "amount": "20000"}],
            cashier  = user,
        )
        return sale, product

    def test_full_return(self):
        sale, product = self._make_sale()
        SaleService.return_sale(sale)

        sale.refresh_from_db()
        assert sale.status == SaleStatus.RETURNED
        product.stock.refresh_from_db()
        assert product.stock.quantity == Decimal("10")  # qaytib keldi

    def test_partial_return(self):
        sale, product = self._make_sale()
        item = sale.items.first()

        SaleService.return_sale(
            sale,
            items_to_return=[{"sale_item_id": item.pk, "quantity": Decimal("2")}],
        )
        sale.refresh_from_db()
        assert sale.status == SaleStatus.PARTIAL
        product.stock.refresh_from_db()
        assert product.stock.quantity == Decimal("8")  # 6 + 2 = 8

    def test_double_return_raises(self):
        sale, _ = self._make_sale()
        SaleService.return_sale(sale)
        sale.refresh_from_db()
        with pytest.raises(BusinessLogicError, match="allaqachon"):
            SaleService.return_sale(sale)

    def test_partial_return_invalid_qty_raises(self):
        sale, _ = self._make_sale()
        item = sale.items.first()
        with pytest.raises(BusinessLogicError, match="Noto'g'ri"):
            SaleService.return_sale(
                sale,
                items_to_return=[{"sale_item_id": item.pk, "quantity": Decimal("99")}],
            )


@pytest.mark.django_db
class TestDailySummary:

    def test_daily_summary_keys(self):
        summary = SaleService.get_daily_summary()
        assert "total_sales"   in summary
        assert "total_revenue" in summary
        assert "total_cash"    in summary
        assert "total_card"    in summary
        assert "total_debt"    in summary

    def test_daily_summary_counts(self):
        from datetime import date
        user    = UserFactory()
        product = ProductFactory(sell_price=Decimal("10000"))
        StockFactory(product=product, quantity=Decimal("50"))

        for _ in range(3):
            fill_cart(user.pk, [(product, Decimal("1"))])
            SaleService.checkout(
                user_id  = user.pk,
                payments = [{"method": PaymentMethod.CASH, "amount": "10000"}],
                cashier  = user,
            )

        summary = SaleService.get_daily_summary(date.today())
        assert summary["total_sales"]   >= 3
        assert Decimal(str(summary["total_revenue"])) >= Decimal("30000")
