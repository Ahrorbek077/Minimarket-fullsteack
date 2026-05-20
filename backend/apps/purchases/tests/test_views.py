"""
Purchases views testlari.
pytest -v purchases/tests/test_views.py
"""
import pytest
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APIClient

from users.models import UserRole
from users.tests.factories import AdminFactory, UserFactory
from companies.tests.factories import CompanyFactory
from products.tests.factories import ProductFactory
from purchases.models import PurchaseStatus
from purchases.services import PurchaseService

BASE = "/api/v1/purchases/"


def client(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


def make_payload(company, products_data):
    return {
        "company_id": company.pk,
        "items": [
            {
                "product_id": p.pk,
                "quantity":   str(qty),
                "cost_price": str(cost),
                "sell_price": str(sell),
            }
            for p, qty, cost, sell in products_data
        ],
    }


@pytest.mark.django_db
class TestPurchaseCreate:

    def test_admin_creates_purchase(self):
        admin   = AdminFactory()
        company = CompanyFactory()
        product = ProductFactory()
        payload = make_payload(company, [(product, "10", "5000", "7000")])
        res = client(admin).post(BASE, payload, format="json")
        assert res.status_code == status.HTTP_201_CREATED
        data = res.json()["data"]
        assert data["status"] == PurchaseStatus.DRAFT
        assert data["total_amount"] == "50000.00"

    def test_cashier_cannot_create(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        res     = client(cashier).post(BASE, {}, format="json")
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_invalid_company_returns_400(self):
        admin   = AdminFactory()
        product = ProductFactory()
        payload = {"company_id": 99999, "items": [{"product_id": product.pk, "quantity": "1", "cost_price": "1000", "sell_price": "1500"}]}
        res = client(admin).post(BASE, payload, format="json")
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_empty_items_returns_400(self):
        admin   = AdminFactory()
        company = CompanyFactory()
        res = client(admin).post(BASE, {"company_id": company.pk, "items": []}, format="json")
        assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPurchaseReceive:

    def test_receive_action(self):
        admin   = AdminFactory()
        company = CompanyFactory()
        product = ProductFactory()
        payload = make_payload(company, [(product, "5", "3000", "4500")])

        create_res = client(admin).post(BASE, payload, format="json")
        purchase_id = create_res.json()["data"]["id"]

        res = client(admin).post(f"{BASE}{purchase_id}/receive/")
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["data"]["status"] == PurchaseStatus.RECEIVED

        product.stock.refresh_from_db()
        assert product.stock.quantity == Decimal("5")


@pytest.mark.django_db
class TestPurchasePay:

    def _create_received(self, admin):
        company = CompanyFactory()
        product = ProductFactory()
        payload = make_payload(company, [(product, "10", "10000", "14000")])
        p_id    = client(admin).post(BASE, payload, format="json").json()["data"]["id"]
        client(admin).post(f"{BASE}{p_id}/receive/")
        return p_id

    def test_pay_partial(self):
        admin = AdminFactory()
        p_id  = self._create_received(admin)
        res   = client(admin).post(f"{BASE}{p_id}/pay/", {"amount": "50000"}, format="json")
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["status"] == PurchaseStatus.PARTIAL

    def test_pay_full(self):
        admin = AdminFactory()
        p_id  = self._create_received(admin)
        res   = client(admin).post(f"{BASE}{p_id}/pay/", {"amount": "100000"}, format="json")
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["status"] == PurchaseStatus.PAID

    def test_overpayment_400(self):
        admin = AdminFactory()
        p_id  = self._create_received(admin)
        res   = client(admin).post(f"{BASE}{p_id}/pay/", {"amount": "999999"}, format="json")
        assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPurchaseCancel:

    def test_cancel_draft(self):
        admin   = AdminFactory()
        company = CompanyFactory()
        product = ProductFactory()
        payload = make_payload(company, [(product, "1", "1000", "1500")])
        p_id    = client(admin).post(BASE, payload, format="json").json()["data"]["id"]
        res     = client(admin).post(f"{BASE}{p_id}/cancel/", {"reason": "Test"}, format="json")
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["status"] == PurchaseStatus.CANCELLED


@pytest.mark.django_db
class TestPurchaseDebts:

    def test_debts_endpoint(self):
        admin   = AdminFactory()
        company = CompanyFactory()
        product = ProductFactory()
        payload = make_payload(company, [(product, "1", "1000", "1500")])
        p_id    = client(admin).post(BASE, payload, format="json").json()["data"]["id"]
        client(admin).post(f"{BASE}{p_id}/receive/")

        res = client(admin).get(f"{BASE}debts/")
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["count"] >= 1
