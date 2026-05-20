"""
Reports querysets testlari.
pytest -v reports/tests/test_querysets.py
"""
import pytest
from datetime import date
from decimal import Decimal

from reports.querysets import (
    get_sales_summary, get_sales_report,
    get_stock_report, get_stock_summary,
    get_top_products, get_purchases_report,
)


@pytest.fixture(autouse=True)
def clear_cache():
    from django.core.cache import cache
    yield
    cache.clear()


@pytest.mark.django_db
class TestSalesQuerysets:

    def test_sales_summary_empty(self):
        today   = date.today()
        summary = get_sales_summary(today, today)
        assert summary["total_sales"]   == 0
        assert summary["total_revenue"] == Decimal("0")

    def test_sales_summary_with_data(self):
        from reports.tests.factories import make_sale
        from sales.models import PaymentMethod
        today = date.today()

        make_sale(amount=Decimal("30000"), method=PaymentMethod.CASH)
        make_sale(amount=Decimal("20000"), method=PaymentMethod.CARD)

        summary = get_sales_summary(today, today)
        assert summary["total_sales"]   >= 2
        assert summary["total_revenue"] >= Decimal("50000")
        assert summary["cash_total"]    >= Decimal("30000")
        assert summary["card_total"]    >= Decimal("20000")

    def test_sales_summary_profit(self):
        from reports.tests.factories import make_sale
        today = date.today()
        make_sale(amount=Decimal("10000"))
        summary = get_sales_summary(today, today)
        assert "gross_profit"  in summary
        assert "profit_margin" in summary

    def test_sales_report_qs(self):
        from reports.tests.factories import make_sale
        today = date.today()
        make_sale()
        qs = get_sales_report(today, today)
        assert qs.count() >= 1

    def test_top_products(self):
        from reports.tests.factories import make_sale
        today = date.today()
        make_sale()
        data = list(get_top_products(today, today, limit=10))
        assert len(data) >= 1
        assert "product__name"  in data[0]
        assert "total_qty"      in data[0]
        assert "total_revenue"  in data[0]


@pytest.mark.django_db
class TestStockQuerysets:

    def test_stock_summary_keys(self):
        summary = get_stock_summary()
        assert "total_items"       in summary
        assert "total_cost_value"  in summary
        assert "total_sell_value"  in summary
        assert "low_stock_count"   in summary
        assert "out_of_stock"      in summary

    def test_stock_report_qs(self):
        from products.tests.factories import ProductFactory
        from inventory.tests.factories import StockFactory
        ProductFactory.create_batch(3)
        qs = list(get_stock_report())
        assert len(qs) >= 3


@pytest.mark.django_db
class TestPurchasesQuerysets:

    def test_purchases_report(self):
        from reports.tests.factories import make_purchase
        from datetime import date
        make_purchase()
        today = date.today()
        qs    = get_purchases_report(today, today)
        assert qs.count() >= 1
