"""
Signal handler testlari — avtomatik logging.
pytest -v history/tests/test_signals.py
"""
import pytest
from decimal import Decimal

from history.models import AuditAction, AuditLog
from users.tests.factories import UserFactory, AdminFactory


@pytest.mark.django_db
class TestAuthSignals:

    def test_login_creates_log(self):
        """Login signali to'g'ri ishlaydi."""
        from django.contrib.auth.signals import user_logged_in
        from django.test import RequestFactory

        user    = UserFactory()
        factory = RequestFactory()
        request = factory.get("/")
        request.META["REMOTE_ADDR"] = "127.0.0.1"

        # Signalni to'g'ridan-to'g'ri chaqiramiz
        count_before = AuditLog.objects.filter(
            action=AuditAction.LOGIN
        ).count()
        user_logged_in.send(sender=user.__class__, request=request, user=user)

        log = AuditLog.objects.filter(
            user=user, action=AuditAction.LOGIN
        ).first()
        assert log is not None
        assert log.extra.get("email") == user.email


@pytest.mark.django_db
class TestUserSignals:

    def test_user_create_logs(self):
        count_before = AuditLog.objects.filter(action=AuditAction.CREATE, model_name="User").count()
        UserFactory()
        count_after  = AuditLog.objects.filter(action=AuditAction.CREATE, model_name="User").count()
        assert count_after == count_before + 1

    def test_user_create_log_has_role(self):
        from users.models import UserRole
        user = UserFactory(role=UserRole.CASHIER)
        log  = AuditLog.objects.filter(
            action=AuditAction.CREATE, model_name="User", object_id=user.pk
        ).first()
        assert log is not None
        assert log.extra.get("role") == UserRole.CASHIER


@pytest.mark.django_db
class TestProductSignals:

    def test_product_create_logs(self):
        from products.tests.factories import ProductFactory
        count_before = AuditLog.objects.filter(action=AuditAction.CREATE, model_name="Product").count()
        ProductFactory()
        count_after  = AuditLog.objects.filter(action=AuditAction.CREATE, model_name="Product").count()
        assert count_after == count_before + 1

    def test_product_log_has_prices(self):
        from products.tests.factories import ProductFactory
        product = ProductFactory(cost_price=Decimal("5000"), sell_price=Decimal("7000"))
        log     = AuditLog.objects.filter(
            action=AuditAction.CREATE, model_name="Product", object_id=product.pk
        ).first()
        assert log is not None
        assert log.extra.get("cost_price") == "5000"
        assert log.extra.get("sell_price") == "7000"


@pytest.mark.django_db
class TestPurchaseSignals:

    def test_purchase_create_logs(self):
        from companies.tests.factories import CompanyFactory
        from products.tests.factories import ProductFactory
        from purchases.services import PurchaseService

        company = CompanyFactory()
        product = ProductFactory()
        count_before = AuditLog.objects.filter(
            action=AuditAction.CREATE, model_name="Purchase"
        ).count()

        PurchaseService.create(
            company    = company,
            items_data = [{"product": product, "quantity": Decimal("5"),
                           "cost_price": Decimal("1000"), "sell_price": Decimal("1500")}],
        )
        count_after = AuditLog.objects.filter(
            action=AuditAction.CREATE, model_name="Purchase"
        ).count()
        assert count_after == count_before + 1

    def test_purchase_receive_logs(self):
        from companies.tests.factories import CompanyFactory
        from products.tests.factories import ProductFactory
        from inventory.tests.factories import StockFactory
        from purchases.services import PurchaseService

        company  = CompanyFactory()
        product  = ProductFactory()
        StockFactory(product=product, quantity=Decimal("0"))

        purchase = PurchaseService.create(
            company    = company,
            items_data = [{"product": product, "quantity": Decimal("10"),
                           "cost_price": Decimal("1000"), "sell_price": Decimal("1500")}],
        )
        PurchaseService.receive(purchase)

        log = AuditLog.objects.filter(
            action=AuditAction.PURCHASE_RECEIVED, object_id=purchase.pk
        ).first()
        assert log is not None


@pytest.mark.django_db
class TestSaleSignals:

    def test_sale_checkout_logs(self):
        from decimal import Decimal
        from inventory.tests.factories import StockFactory
        from products.tests.factories import ProductFactory
        from sales.cart import CartService
        from sales.models import PaymentMethod
        from sales.services import SaleService

        from django.core.cache import cache
        cache.clear()

        user    = UserFactory()
        product = ProductFactory(sell_price=Decimal("5000"))
        StockFactory(product=product, quantity=Decimal("10"))  # ← muhim
        CartService.add_item(user.pk, product.pk, Decimal("2"))

        count_before = AuditLog.objects.filter(action=AuditAction.SALE_CHECKOUT).count()
        sale = SaleService.checkout(
            user_id  = user.pk,
            payments = [{"method": PaymentMethod.CASH, "amount": "10000"}],
            cashier  = user,
        )
        count_after = AuditLog.objects.filter(action=AuditAction.SALE_CHECKOUT).count()
        assert count_after == count_before + 1

        log = AuditLog.objects.filter(
            action=AuditAction.SALE_CHECKOUT, object_id=sale.pk
        ).first()
        assert log.extra.get("invoice_no") == sale.invoice_no

        cache.clear()
