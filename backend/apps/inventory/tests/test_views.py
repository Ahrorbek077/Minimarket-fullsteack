"""
Inventory views testlari.
pytest -v inventory/tests/test_views.py
"""
import pytest
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APIClient

from users.models import UserRole
from users.tests.factories import AdminFactory, UserFactory
from products.tests.factories import ProductFactory
from .factories import StockFactory, StockMovementFactory

STOCK_URL = "/api/v1/inventory/stock/"
MOVES_URL = "/api/v1/inventory/movements/"


def client(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@pytest.mark.django_db
class TestStockViews:

    def test_storekeeper_can_list(self):
        storekeeper = UserFactory(role=UserRole.STOREKEEPER)
        ProductFactory.create_batch(3)
        res = client(storekeeper).get(STOCK_URL)
        assert res.status_code == status.HTTP_200_OK

    def test_cashier_forbidden(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        res = client(cashier).get(STOCK_URL)
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_low_stock_endpoint(self):
        storekeeper = UserFactory(role=UserRole.STOREKEEPER)
        low = ProductFactory(min_stock=Decimal("20"))
        StockFactory(product=low, quantity=Decimal("3"))
        res = client(storekeeper).get(STOCK_URL + "low-stock/")
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["count"] >= 1

    def test_summary_admin_only(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        res = client(cashier).get(STOCK_URL + "summary/")
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_summary_returns_keys(self):
        admin = AdminFactory()
        res   = client(admin).get(STOCK_URL + "summary/")
        assert res.status_code == status.HTTP_200_OK
        data  = res.json()["data"]
        assert "total_products"  in data
        assert "low_stock_count" in data

    def test_adjust_stock(self):
        admin   = AdminFactory()
        product = ProductFactory()
        stock   = product.stock  # signal orqali yaratilgan
        res = client(admin).post(
            f"{STOCK_URL}{stock.pk}/adjust/",
            {"new_quantity": "75.00", "reason": "Test sanoq"},
            format="json",
        )
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["success"] is True
        stock.refresh_from_db()
        assert stock.quantity == Decimal("75")

    def test_adjust_negative_returns_400(self):
        admin   = AdminFactory()
        product = ProductFactory()
        stock   = product.stock
        res = client(admin).post(
            f"{STOCK_URL}{stock.pk}/adjust/",
            {"new_quantity": "-10"},
            format="json",
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_adjust_only_admin(self):
        storekeeper = UserFactory(role=UserRole.STOREKEEPER)
        product     = ProductFactory()
        stock       = product.stock
        res = client(storekeeper).post(
            f"{STOCK_URL}{stock.pk}/adjust/",
            {"new_quantity": "10"},
            format="json",
        )
        assert res.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestMovementViews:

    def test_list_movements(self):
        storekeeper = UserFactory(role=UserRole.STOREKEEPER)
        StockMovementFactory.create_batch(3)
        res = client(storekeeper).get(MOVES_URL)
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["count"] >= 3

    def test_filter_by_product(self):
        storekeeper = UserFactory(role=UserRole.STOREKEEPER)
        p1 = ProductFactory()
        p2 = ProductFactory()
        StockMovementFactory(product=p1)
        StockMovementFactory(product=p2)
        res = client(storekeeper).get(MOVES_URL + f"?product={p1.pk}")
        assert res.status_code == status.HTTP_200_OK
        for mv in res.json()["results"]:
            assert mv["product"] == p1.pk

    def test_cannot_create_movement_directly(self):
        """Movement faqat service orqali yaratiladi — POST yo'q."""
        storekeeper = UserFactory(role=UserRole.STOREKEEPER)
        res = client(storekeeper).post(MOVES_URL, {}, format="json")
        assert res.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
