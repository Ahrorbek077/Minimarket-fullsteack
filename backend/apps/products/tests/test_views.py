"""
Products views testlari — CRUD, barcode, permissions.
pytest -v apps/products/tests/test_views.py
"""
import pytest
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APIClient

from users.models import UserRole
from users.tests.factories import UserFactory, AdminFactory, SuperAdminFactory
from .factories import CategoryFactory, ProductFactory, UnitFactory

PRODUCTS_URL  = "/api/v1/products/products/"
CATEGORIES_URL = "/api/v1/products/categories/"
UNITS_URL     = "/api/v1/products/units/"


def get_client(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


# ─── Products ─────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestProductList:

    def test_cashier_can_list(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        ProductFactory.create_batch(3)
        res = get_client(cashier).get(PRODUCTS_URL)
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["count"] >= 3

    def test_unauthenticated_forbidden(self):
        res = APIClient().get(PRODUCTS_URL)
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_filter_by_name(self):
        ProductFactory(name="Lipton choy")
        ProductFactory(name="Coca-Cola")
        admin = AdminFactory()
        res = get_client(admin).get(PRODUCTS_URL + "?name=lipton")
        assert res.status_code == status.HTTP_200_OK
        names = [p["name"] for p in res.json()["results"]]
        assert all("lipton" in n.lower() for n in names)

    def test_filter_by_active(self):
        ProductFactory(is_active=True)
        ProductFactory(is_active=False)
        admin = AdminFactory()
        res = get_client(admin).get(PRODUCTS_URL + "?is_active=true")
        assert res.status_code == status.HTTP_200_OK
        for p in res.json()["results"]:
            assert p["is_active"] is True


@pytest.mark.django_db
class TestProductCreate:

    def test_admin_creates_product(self):
        admin    = AdminFactory()
        category = CategoryFactory()
        unit     = UnitFactory()
        payload  = {
            "name":       "Yangi mahsulot",
            "barcode":    "9876543210000",
            "cost_price": "5000.00",
            "sell_price": "6500.00",
            "category_id": category.pk,
            "unit_id":     unit.pk,
        }
        res = get_client(admin).post(PRODUCTS_URL, payload, format="json")
        assert res.status_code == status.HTTP_201_CREATED

    def test_cashier_cannot_create(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        res = get_client(cashier).post(PRODUCTS_URL, {"name": "x"}, format="json")
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_duplicate_barcode_returns_400(self):
        admin = AdminFactory()
        ProductFactory(barcode="111111111")
        res = get_client(admin).post(
            PRODUCTS_URL,
            {"name": "B", "barcode": "111111111", "sell_price": "100"},
            format="json",
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_sell_price_less_than_cost_returns_400(self):
        admin = AdminFactory()
        res = get_client(admin).post(
            PRODUCTS_URL,
            {"name": "C", "cost_price": "10000", "sell_price": "5000"},
            format="json",
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestProductSoftDelete:

    def test_soft_delete(self):
        admin   = AdminFactory()
        product = ProductFactory()
        res = get_client(admin).delete(f"{PRODUCTS_URL}{product.pk}/")
        assert res.status_code == status.HTTP_200_OK
        product.refresh_from_db()
        assert product.deleted_at is not None

    def test_deleted_not_in_list(self):
        admin   = AdminFactory()
        product = ProductFactory()
        get_client(admin).delete(f"{PRODUCTS_URL}{product.pk}/")
        res = get_client(admin).get(PRODUCTS_URL)
        ids = [p["id"] for p in res.json()["results"]]
        assert product.pk not in ids


@pytest.mark.django_db
class TestBarcodeEndpoint:

    def test_get_by_barcode_success(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        product = ProductFactory(barcode="5901234567890", is_active=True)
        res = get_client(cashier).get(
            f"{PRODUCTS_URL}barcode/5901234567890/"
        )
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["data"]["barcode"] == "5901234567890"

    def test_get_by_barcode_not_found(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        res = get_client(cashier).get(
            f"{PRODUCTS_URL}barcode/0000000000000/"
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_inactive_product_not_found_by_barcode(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        product = ProductFactory(barcode="9999999999999", is_active=False)
        res = get_client(cashier).get(
            f"{PRODUCTS_URL}barcode/9999999999999/"
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUpdatePrice:

    def test_update_price(self):
        admin   = AdminFactory()
        product = ProductFactory(cost_price=Decimal("5000"), sell_price=Decimal("6000"))
        res = get_client(admin).patch(
            f"{PRODUCTS_URL}{product.pk}/update-price/",
            {"sell_price": "8000.00"},
            format="json",
        )
        assert res.status_code == status.HTTP_200_OK
        product.refresh_from_db()
        assert product.sell_price == Decimal("8000.00")

    def test_no_price_field_returns_400(self):
        admin   = AdminFactory()
        product = ProductFactory()
        res = get_client(admin).patch(
            f"{PRODUCTS_URL}{product.pk}/update-price/",
            {},
            format="json",
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST


# ─── Categories ───────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestCategoryViews:

    def test_list_categories(self):
        admin = AdminFactory()
        CategoryFactory.create_batch(3)
        res = get_client(admin).get(CATEGORIES_URL)
        assert res.status_code == status.HTTP_200_OK

    def test_create_category(self):
        admin = AdminFactory()
        res = get_client(admin).post(
            CATEGORIES_URL,
            {"name": "Yangi kategoriya", "icon": "🛒"},
            format="json",
        )
        assert res.status_code == status.HTTP_201_CREATED

    def test_create_subcategory(self):
        admin  = AdminFactory()
        parent = CategoryFactory()
        res = get_client(admin).post(
            CATEGORIES_URL,
            {"name": "Ichki", "parent": parent.pk},
            format="json",
        )
        assert res.status_code == status.HTTP_201_CREATED

    def test_tree_endpoint(self):
        admin  = AdminFactory()
        parent = CategoryFactory()
        CategoryFactory(parent=parent)   # child
        res = get_client(admin).get(CATEGORIES_URL + "tree/")
        assert res.status_code == status.HTTP_200_OK
        assert "data" in res.json()


# ─── Units ─────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestUnitViews:

    def test_list_units(self):
        admin = AdminFactory()
        UnitFactory.create_batch(3)
        res = get_client(admin).get(UNITS_URL)
        assert res.status_code == status.HTTP_200_OK

    def test_create_unit(self):
        admin = AdminFactory()
        res = get_client(admin).post(
            UNITS_URL,
            {"name": "Kilogram", "short_name": "kg"},
            format="json",
        )
        assert res.status_code == status.HTTP_201_CREATED

    def test_cashier_cannot_create_unit(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        res = get_client(cashier).post(
            UNITS_URL,
            {"name": "Metr", "short_name": "m"},
            format="json",
        )
        assert res.status_code == status.HTTP_403_FORBIDDEN
