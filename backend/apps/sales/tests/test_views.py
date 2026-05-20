"""
Sales views testlari.
pytest -v sales/tests/test_views.py
"""
import pytest
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APIClient

from inventory.tests.factories import StockFactory
from products.tests.factories import ProductFactory
from sales.cart import CartService
from sales.models import PaymentMethod, SaleStatus
from sales.services import SaleService
from users.models import UserRole
from users.tests.factories import AdminFactory, UserFactory

CART_URL  = "/api/v1/sales/cart/"
SALES_URL = "/api/v1/sales/"


def client(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@pytest.fixture(autouse=True)
def clear_cache():
    from django.core.cache import cache
    yield
    cache.clear()


# ─── Cart endpoints ────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestCartEndpoints:

    def test_get_empty_cart(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        res = client(cashier).get(f"{CART_URL}cart/")
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["data"]["item_count"] == 0

    def test_add_item(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        product = ProductFactory(sell_price=Decimal("5000"))
        StockFactory(product=product, quantity=Decimal("10"))

        res = client(cashier).post(
            f"{CART_URL}add/",
            {"product_id": product.pk, "quantity": "2"},
            format="json",
        )
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["data"]["item_count"] == 1

    def test_scan_barcode(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        product = ProductFactory(barcode="5555555555555")
        StockFactory(product=product, quantity=Decimal("10"))

        res = client(cashier).post(
            f"{CART_URL}scan/",
            {"barcode": "5555555555555", "quantity": "1"},
            format="json",
        )
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["data"]["item_count"] == 1

    def test_scan_invalid_barcode(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        res = client(cashier).post(
            f"{CART_URL}scan/",
            {"barcode": "0000000000000"},
            format="json",
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_item(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        product = ProductFactory(sell_price=Decimal("3000"))
        StockFactory(product=product, quantity=Decimal("10"))
        CartService.add_item(cashier.pk, product.pk, Decimal("5"))

        res = client(cashier).patch(
            f"{CART_URL}update/{product.pk}/",
            {"quantity": "3"},
            format="json",
        )
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["data"]["items"][0]["quantity"] == "3.00"

    def test_remove_item(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        product = ProductFactory()
        StockFactory(product=product, quantity=Decimal("10"))
        CartService.add_item(cashier.pk, product.pk, Decimal("2"))

        res = client(cashier).delete(f"{CART_URL}remove/{product.pk}/")
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["data"]["item_count"] == 0

    def test_clear_cart(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        product = ProductFactory()
        StockFactory(product=product, quantity=Decimal("10"))
        CartService.add_item(cashier.pk, product.pk, Decimal("1"))

        res = client(cashier).delete(f"{CART_URL}clear/")
        assert res.status_code == status.HTTP_200_OK

    def test_unauthenticated_forbidden(self):
        res = APIClient().get(f"{CART_URL}cart/")
        assert res.status_code == status.HTTP_401_UNAUTHORIZED


# ─── Checkout ─────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestCheckoutEndpoint:

    def test_checkout_success(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        product = ProductFactory(sell_price=Decimal("8000"))
        StockFactory(product=product, quantity=Decimal("10"))
        CartService.add_item(cashier.pk, product.pk, Decimal("2"))

        res = client(cashier).post(
            f"{SALES_URL}checkout/",
            {"payments": [{"method": "cash", "amount": "16000"}]},
            format="json",
        )
        assert res.status_code == status.HTTP_201_CREATED
        data = res.json()["data"]
        assert data["status"]     == SaleStatus.COMPLETED
        assert data["net_amount"] == "16000.00"

    def test_checkout_with_discount(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        product = ProductFactory(sell_price=Decimal("10000"))
        StockFactory(product=product, quantity=Decimal("5"))
        CartService.add_item(cashier.pk, product.pk, Decimal("1"))

        res = client(cashier).post(
            f"{SALES_URL}checkout/",
            {
                "payments": [{"method": "cash", "amount": "9000"}],
                "discount_pct": "10",
            },
            format="json",
        )
        assert res.status_code == status.HTTP_201_CREATED
        assert res.json()["data"]["net_amount"] == "9000.00"

    def test_checkout_empty_cart(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        res = client(cashier).post(
            f"{SALES_URL}checkout/",
            {"payments": [{"method": "cash", "amount": "1000"}]},
            format="json",
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_checkout_insufficient_payment(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        product = ProductFactory(sell_price=Decimal("10000"))
        StockFactory(product=product, quantity=Decimal("5"))
        CartService.add_item(cashier.pk, product.pk, Decimal("1"))

        res = client(cashier).post(
            f"{SALES_URL}checkout/",
            {"payments": [{"method": "cash", "amount": "5000"}]},
            format="json",
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST


# ─── Sales list / detail ──────────────────────────────────────────────────────

@pytest.mark.django_db
class TestSaleListDetail:

    def _make_sale(self, user):
        product = ProductFactory(sell_price=Decimal("5000"))
        StockFactory(product=product, quantity=Decimal("10"))
        CartService.add_item(user.pk, product.pk, Decimal("2"))
        return SaleService.checkout(
            user_id  = user.pk,
            payments = [{"method": PaymentMethod.CASH, "amount": "10000"}],
            cashier  = user,
        )

    def test_list_sales(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        self._make_sale(cashier)
        res = client(cashier).get(SALES_URL)
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["count"] >= 1

    def test_retrieve_sale(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        sale    = self._make_sale(cashier)
        res = client(cashier).get(f"{SALES_URL}{sale.pk}/")
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["invoice_no"] == sale.invoice_no


# ─── Return ───────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestReturnEndpoint:

    def _make_sale(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        product = ProductFactory(sell_price=Decimal("5000"))
        StockFactory(product=product, quantity=Decimal("10"))
        CartService.add_item(cashier.pk, product.pk, Decimal("3"))
        sale = SaleService.checkout(
            user_id  = cashier.pk,
            payments = [{"method": PaymentMethod.CASH, "amount": "15000"}],
            cashier  = cashier,
        )
        return sale

    def test_full_return(self):
        admin = AdminFactory()
        sale  = self._make_sale()
        res   = client(admin).post(
            f"{SALES_URL}{sale.pk}/return/",
            {"reason": "Mijoz qaytardi"},
            format="json",
        )
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["data"]["status"] == SaleStatus.RETURNED

    def test_cashier_cannot_return(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        sale    = self._make_sale()
        res     = client(cashier).post(f"{SALES_URL}{sale.pk}/return/", {}, format="json")
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_daily_summary(self):
        admin = AdminFactory()
        res   = client(admin).get(f"{SALES_URL}daily-summary/")
        assert res.status_code == status.HTTP_200_OK
        assert "total_sales" in res.json()["data"]
