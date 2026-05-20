"""
Reports views testlari.
pytest -v reports/tests/test_views.py
"""
import pytest
from datetime import date
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APIClient

from users.models import UserRole
from users.tests.factories import AdminFactory, UserFactory

BASE = "/api/v1/reports/"


def client(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@pytest.fixture(autouse=True)
def clear_cache():
    from django.core.cache import cache
    yield
    cache.clear()


@pytest.mark.django_db
class TestReportPermissions:

    def test_cashier_forbidden(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        res     = client(cashier).get(f"{BASE}sales/summary/")
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_accountant_can_view(self):
        accountant = UserFactory(role=UserRole.ACCOUNTANT)
        today      = date.today().isoformat()
        res        = client(accountant).get(
            f"{BASE}sales/summary/?date_from={today}&date_to={today}"
        )
        assert res.status_code == status.HTTP_200_OK

    def test_accountant_cannot_export(self):
        accountant = UserFactory(role=UserRole.ACCOUNTANT)
        today      = date.today().isoformat()
        res        = client(accountant).get(
            f"{BASE}export/?file_format=excel&type=sales&date_from={today}&date_to={today}"
        )
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_export(self):
        admin = AdminFactory()
        today = date.today().isoformat()
        res   = client(admin).get(
            f"{BASE}export/?file_format=excel&type=sales&date_from={today}&date_to={today}"
        )
        assert res.status_code == status.HTTP_200_OK

    def test_unauthenticated_forbidden(self):
        res = APIClient().get(f"{BASE}sales/summary/")
        assert res.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestSalesReports:

    def test_sales_summary_response_keys(self):
        admin = AdminFactory()
        today = date.today().isoformat()
        res   = client(admin).get(
            f"{BASE}sales/summary/?date_from={today}&date_to={today}"
        )
        assert res.status_code == status.HTTP_200_OK
        data = res.json()["data"]
        assert "total_sales"   in data
        assert "total_revenue" in data
        assert "gross_profit"  in data

    def test_sales_chart_daily(self):
        admin = AdminFactory()
        today = date.today().isoformat()
        res   = client(admin).get(
            f"{BASE}sales/chart/?date_from={today}&date_to={today}&period=daily"
        )
        assert res.status_code == status.HTTP_200_OK

    def test_sales_chart_invalid_period(self):
        admin = AdminFactory()
        today = date.today().isoformat()
        res   = client(admin).get(
            f"{BASE}sales/chart/?date_from={today}&date_to={today}&period=yearly"
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_top_products(self):
        admin = AdminFactory()
        today = date.today().isoformat()
        res   = client(admin).get(
            f"{BASE}sales/top-products/?date_from={today}&date_to={today}&limit=10"
        )
        assert res.status_code == status.HTTP_200_OK
        assert "count" in res.json()
        assert "data"  in res.json()


@pytest.mark.django_db
class TestStockReport:

    def test_stock_summary(self):
        admin = AdminFactory()
        res   = client(admin).get(f"{BASE}stock/summary/")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()["data"]
        assert "total_items"      in data
        assert "total_cost_value" in data
        assert "low_stock_count"  in data


@pytest.mark.django_db
class TestExportEndpoint:

    def test_excel_sales_export(self):
        admin = AdminFactory()
        today = date.today().isoformat()
        res   = client(admin).get(
            f"{BASE}export/?file_format=excel&type=sales&date_from={today}&date_to={today}"
        )
        assert res.status_code == status.HTTP_200_OK
        assert "spreadsheetml" in res["Content-Type"]
        assert res["Content-Disposition"].endswith(".xlsx\"")

    def test_pdf_sales_export(self):
        admin = AdminFactory()
        today = date.today().isoformat()
        res   = client(admin).get(
            f"{BASE}export/?file_format=pdf&type=sales&date_from={today}&date_to={today}"
        )
        assert res.status_code == status.HTTP_200_OK
        assert res["Content-Type"] == "application/pdf"
        assert res["Content-Disposition"].endswith(".pdf\"")

    def test_excel_stock_export(self):
        admin = AdminFactory()
        today = date.today().isoformat()
        res   = client(admin).get(
            f"{BASE}export/?file_format=excel&type=stock&date_from={today}&date_to={today}"
        )
        assert res.status_code == status.HTTP_200_OK
        assert "spreadsheetml" in res["Content-Type"]

    def test_invalid_date_range(self):
        admin = AdminFactory()
        res   = client(admin).get(
            f"{BASE}export/?file_format=excel&type=sales&date_from=2024-12-31&date_to=2024-01-01"
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_date_range_over_1_year(self):
        admin = AdminFactory()
        res   = client(admin).get(
            f"{BASE}export/?file_format=excel&type=sales&date_from=2023-01-01&date_to=2025-01-02"
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST
