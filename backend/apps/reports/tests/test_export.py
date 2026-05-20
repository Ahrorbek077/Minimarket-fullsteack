"""
Excel va PDF export testlari.
pytest -v reports/tests/test_export.py
"""
import pytest
from datetime import date
from decimal import Decimal


@pytest.fixture(autouse=True)
def clear_cache():
    from django.core.cache import cache
    yield
    cache.clear()


@pytest.mark.django_db
class TestExcelExport:

    def test_sales_excel_returns_bytes(self):
        from reports.tests.factories import make_sale
        from reports.excel import export_sales_excel
        from reports.querysets import get_sales_report, get_sales_summary

        today = date.today()
        make_sale(amount=Decimal("15000"))

        qs      = get_sales_report(today, today)
        summary = get_sales_summary(today, today)
        buf     = export_sales_excel(qs, today, today, summary)

        assert buf is not None
        content = buf.read()
        assert len(content) > 0
        # Excel magic bytes: PK zip header
        assert content[:2] == b"PK"

    def test_sales_excel_empty_data(self):
        from reports.excel import export_sales_excel
        from reports.querysets import get_sales_report, get_sales_summary
        from sales.models import Sale

        today   = date.today()
        qs      = Sale.objects.none()
        summary = get_sales_summary(today, today)
        buf     = export_sales_excel(qs, today, today, summary)
        assert buf.read()[:2] == b"PK"

    def test_stock_excel_returns_bytes(self):
        from reports.excel import export_stock_excel
        from reports.querysets import get_stock_report, get_stock_summary
        from products.tests.factories import ProductFactory

        ProductFactory.create_batch(3)
        qs      = get_stock_report()
        summary = get_stock_summary()
        buf     = export_stock_excel(qs, summary)
        assert buf.read()[:2] == b"PK"

    def test_purchases_excel_returns_bytes(self):
        from reports.excel import export_purchases_excel
        from reports.tests.factories import make_purchase
        from reports.querysets import get_purchases_report

        today = date.today()
        make_purchase()
        qs  = get_purchases_report(today, today)
        buf = export_purchases_excel(qs, today, today)
        assert buf.read()[:2] == b"PK"

    def test_top_products_excel(self):
        from reports.excel import export_top_products_excel
        from reports.tests.factories import make_sale
        from reports.querysets import get_top_products

        today = date.today()
        make_sale()
        data = list(get_top_products(today, today, 10))
        buf  = export_top_products_excel(data, today, today)
        assert buf.read()[:2] == b"PK"


@pytest.mark.django_db
class TestPDFExport:

    def test_sales_pdf_returns_bytes(self):
        from reports.tests.factories import make_sale
        from reports.pdf import export_sales_pdf
        from reports.querysets import get_sales_report, get_sales_summary

        today = date.today()
        make_sale(amount=Decimal("20000"))

        qs      = get_sales_report(today, today)
        summary = get_sales_summary(today, today)
        buf     = export_sales_pdf(qs, today, today, summary)

        content = buf.read()
        assert len(content) > 0
        assert content[:4] == b"%PDF"

    def test_stock_pdf_returns_bytes(self):
        from reports.pdf import export_stock_pdf
        from reports.querysets import get_stock_report, get_stock_summary
        from products.tests.factories import ProductFactory

        ProductFactory.create_batch(2)
        qs      = get_stock_report()
        summary = get_stock_summary()
        buf     = export_stock_pdf(qs, summary)
        assert buf.read()[:4] == b"%PDF"

    def test_purchases_pdf_returns_bytes(self):
        from reports.pdf import export_purchases_pdf
        from reports.tests.factories import make_purchase
        from reports.querysets import get_purchases_report

        today = date.today()
        make_purchase()
        qs  = get_purchases_report(today, today)
        buf = export_purchases_pdf(qs, today, today)
        assert buf.read()[:4] == b"%PDF"
