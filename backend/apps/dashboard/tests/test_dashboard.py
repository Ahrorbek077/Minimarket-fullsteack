"""
Dashboard API testlari.
pytest -v apps/dashboard/tests/test_dashboard.py
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta

from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APIClient

from users.models import UserRole
from users.tests.factories import AdminFactory, UserFactory

DASHBOARD_URL = "/api/v1/dashboard/"
PERIOD_URL    = "/api/v1/dashboard/period/"


def client(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@pytest.fixture(autouse=True)
def clear_cache():
    yield
    cache.clear()


# ─── DashboardView ────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestDashboardView:

    def test_cashier_can_access(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        res = client(cashier).get(DASHBOARD_URL)
        assert res.status_code == status.HTTP_200_OK

    def test_admin_can_access(self):
        res = client(AdminFactory()).get(DASHBOARD_URL)
        assert res.status_code == status.HTTP_200_OK

    def test_unauthenticated_forbidden(self):
        res = APIClient().get(DASHBOARD_URL)
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_response_structure(self):
        res = client(AdminFactory()).get(DASHBOARD_URL)
        assert res.status_code == status.HTTP_200_OK
        data = res.json()["data"]

        # Barcha kerakli kalitlar mavjud
        assert "today"        in data
        assert "week"         in data
        assert "month"        in data
        assert "year"         in data
        assert "stock"        in data
        assert "debts"        in data
        assert "top_products" in data
        assert "sales_chart"  in data
        assert "recent_sales" in data
        assert "low_stock"    in data

    def test_today_stats_keys(self):
        res = client(AdminFactory()).get(DASHBOARD_URL)
        today = res.json()["data"]["today"]
        assert "sales_count"  in today
        assert "revenue"      in today
        assert "gross_profit" in today
        assert "debt"         in today
        assert "cash"         in today
        assert "card"         in today
        assert "period"       in today

    def test_stock_overview_keys(self):
        res = client(AdminFactory()).get(DASHBOARD_URL)
        stock = res.json()["data"]["stock"]
        assert "total_products"  in stock
        assert "low_stock_count" in stock
        assert "out_of_stock"    in stock
        assert "cost_value"      in stock
        assert "sell_value"      in stock

    def test_debts_overview_keys(self):
        res = client(AdminFactory()).get(DASHBOARD_URL)
        debts = res.json()["data"]["debts"]
        assert "count"         in debts
        assert "total_debt"    in debts
        assert "overdue_count" in debts
        assert "overdue_debt"  in debts

    def test_sales_chart_length_default(self):
        """Default 7 kun grafik."""
        res = client(AdminFactory()).get(DASHBOARD_URL)
        chart = res.json()["data"]["sales_chart"]
        assert len(chart) == 7

    def test_sales_chart_custom_days(self):
        """?chart_days=14 — 14 kun."""
        res = client(AdminFactory()).get(f"{DASHBOARD_URL}?chart_days=14")
        chart = res.json()["data"]["sales_chart"]
        assert len(chart) == 14

    def test_sales_chart_max_30(self):
        """Max 30 kun — 999 berilsa ham 30 qaytadi."""
        res = client(AdminFactory()).get(f"{DASHBOARD_URL}?chart_days=999")
        chart = res.json()["data"]["sales_chart"]
        assert len(chart) == 30

    def test_sales_chart_dates_sequential(self):
        """Grafik sanalar ketma-ket bo'lishi kerak."""
        res = client(AdminFactory()).get(DASHBOARD_URL)
        chart = res.json()["data"]["sales_chart"]
        dates = [item["date"] for item in chart]
        assert dates == sorted(dates)

    def test_sales_chart_includes_today(self):
        """Bugun grafik da bo'lishi kerak (UTC/local farqini hisobga olgan holda)."""
        from django.utils import timezone
        res   = client(AdminFactory()).get(DASHBOARD_URL)
        chart = res.json()["data"]["sales_chart"]
        today_utc   = str(timezone.now().date())
        today_local = str(date.today())
        dates = [item["date"] for item in chart]
        assert today_utc in dates or today_local in dates

    def test_empty_database_returns_zeros(self):
        """Bo'sh DB da ham 0 qaytaradi, xato bermaydi."""
        res = client(AdminFactory()).get(DASHBOARD_URL)
        assert res.status_code == status.HTTP_200_OK
        today = res.json()["data"]["today"]
        assert today["sales_count"] == 0
        assert today["revenue"] == "0.00"


@pytest.mark.django_db
class TestDashboardWithData:
    """Haqiqiy sotuv ma'lumotlari bilan testlar."""

    def _make_sale(self, cashier=None, amount=Decimal("10000")):
        from inventory.tests.factories import StockFactory
        from products.tests.factories import ProductFactory
        from sales.cart import CartService
        from sales.models import PaymentMethod
        from sales.services import SaleService

        if cashier is None:
            cashier = UserFactory()
        product = ProductFactory(sell_price=amount, cost_price=amount * Decimal("0.7"))
        StockFactory(product=product, quantity=Decimal("50"))
        CartService.add_item(cashier.pk, product.pk, Decimal("1"))
        sale = SaleService.checkout(
            user_id  = cashier.pk,
            payments = [{"method": PaymentMethod.CASH, "amount": str(amount)}],
            cashier  = cashier,
        )
        CartService.clear(cashier.pk)
        return sale

    def test_today_sales_count(self):
        admin = AdminFactory()
        self._make_sale()
        self._make_sale()
        res = client(admin).get(DASHBOARD_URL)
        assert res.json()["data"]["today"]["sales_count"] >= 2

    def test_today_revenue_correct(self):
        admin  = AdminFactory()
        self._make_sale(amount=Decimal("15000"))
        res    = client(admin).get(DASHBOARD_URL)
        today  = res.json()["data"]["today"]
        assert Decimal(today["revenue"]) >= Decimal("15000")

    def test_top_products_today(self):
        admin = AdminFactory()
        self._make_sale()
        res = client(admin).get(DASHBOARD_URL)
        top = res.json()["data"]["top_products"]
        assert isinstance(top, list)

    def test_recent_sales(self):
        admin = AdminFactory()
        self._make_sale()
        res = client(admin).get(DASHBOARD_URL)
        recent = res.json()["data"]["recent_sales"]
        assert len(recent) >= 1
        assert "invoice_no" in recent[0]
        assert "net_amount" in recent[0]

    def test_week_includes_today(self):
        """Haftalik statistika bugungini ham o'z ichiga oladi."""
        admin = AdminFactory()
        self._make_sale(amount=Decimal("20000"))
        res   = client(admin).get(DASHBOARD_URL)
        week  = res.json()["data"]["week"]
        today = res.json()["data"]["today"]
        # Haftalik >= bugungi
        assert Decimal(week["revenue"]) >= Decimal(today["revenue"])


@pytest.mark.django_db
class TestDashboardLowStock:

    def test_low_stock_alerts(self):
        from inventory.tests.factories import StockFactory
        from products.tests.factories import ProductFactory

        # Min qoldiqdan past mahsulot
        low_product = ProductFactory(min_stock=Decimal("20"))
        StockFactory(product=low_product, quantity=Decimal("3"))

        res = client(AdminFactory()).get(DASHBOARD_URL)
        low = res.json()["data"]["low_stock"]
        assert isinstance(low, list)
        product_ids = [item["product__id"] for item in low]
        assert low_product.pk in product_ids

    def test_low_stock_limit(self):
        """Max 5 ta ogohlantirish qaytadi."""
        res = client(AdminFactory()).get(DASHBOARD_URL)
        assert len(res.json()["data"]["low_stock"]) <= 5


# ─── PeriodStatsView ──────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestPeriodStatsView:

    def test_today(self):
        res = client(AdminFactory()).get(f"{PERIOD_URL}?period=today")
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["data"]["period"] == "today"

    def test_week(self):
        res = client(AdminFactory()).get(f"{PERIOD_URL}?period=week")
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["data"]["period"] == "week"

    def test_month(self):
        res = client(AdminFactory()).get(f"{PERIOD_URL}?period=month")
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["data"]["period"] == "month"

    def test_year(self):
        res = client(AdminFactory()).get(f"{PERIOD_URL}?period=year")
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["data"]["period"] == "year"

    def test_invalid_period(self):
        res = client(AdminFactory()).get(f"{PERIOD_URL}?period=invalid")
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_default_period_is_today(self):
        res = client(AdminFactory()).get(PERIOD_URL)
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["data"]["period"] == "today"
