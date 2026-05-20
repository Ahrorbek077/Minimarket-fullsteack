"""
PurchaseService testlari.
pytest -v purchases/tests/test_services.py
"""
import pytest
from decimal import Decimal

from core.exceptions import BusinessLogicError
from inventory.models import MovementType, StockMovement
from inventory.services import StockService
from products.tests.factories import ProductFactory
from companies.tests.factories import CompanyFactory
from users.tests.factories import AdminFactory
from purchases.models import PurchaseStatus
from purchases.services import PurchaseService


def make_items(products_data):
    """Helper: items_data ro'yxati."""
    return [
        {
            "product":    p,
            "quantity":   qty,
            "cost_price": cost,
            "sell_price": sell,
        }
        for p, qty, cost, sell in products_data
    ]


@pytest.mark.django_db
class TestPurchaseCreate:

    def test_create_draft(self):
        company = CompanyFactory()
        product = ProductFactory()
        items   = make_items([(product, Decimal("10"), Decimal("5000"), Decimal("7000"))])
        purchase = PurchaseService.create(company=company, items_data=items)

        assert purchase.status       == PurchaseStatus.DRAFT
        assert purchase.total_amount == Decimal("50000")
        assert purchase.debt_amount  == Decimal("50000")
        assert purchase.paid_amount  == Decimal("0")
        assert purchase.items.count() == 1

    def test_create_multi_items(self):
        company = CompanyFactory()
        p1, p2  = ProductFactory(), ProductFactory()
        items   = make_items([
            (p1, Decimal("5"),  Decimal("2000"), Decimal("3000")),
            (p2, Decimal("10"), Decimal("1000"), Decimal("1500")),
        ])
        purchase = PurchaseService.create(company=company, items_data=items)
        assert purchase.total_amount == Decimal("20000")  # 5*2000 + 10*1000
        assert purchase.items.count() == 2

    def test_create_empty_items_raises(self):
        company = CompanyFactory()
        with pytest.raises(BusinessLogicError, match="bitta mahsulot"):
            PurchaseService.create(company=company, items_data=[])

    def test_create_with_due_date(self):
        from datetime import date, timedelta
        company  = CompanyFactory()
        product  = ProductFactory()
        due_date = date.today() + timedelta(days=30)
        items    = make_items([(product, Decimal("1"), Decimal("1000"), Decimal("1200"))])
        purchase = PurchaseService.create(
            company=company, items_data=items, due_date=due_date
        )
        assert purchase.due_date == due_date


@pytest.mark.django_db
class TestPurchaseReceive:

    def test_receive_adds_to_stock(self):
        company = CompanyFactory()
        product = ProductFactory()
        items   = make_items([(product, Decimal("20"), Decimal("5000"), Decimal("7000"))])
        purchase = PurchaseService.create(company=company, items_data=items)

        PurchaseService.receive(purchase)

        product.stock.refresh_from_db()
        assert product.stock.quantity == Decimal("20")

    def test_receive_creates_stock_movement(self):
        company = CompanyFactory()
        product = ProductFactory()
        items   = make_items([(product, Decimal("15"), Decimal("3000"), Decimal("4500"))])
        purchase = PurchaseService.create(company=company, items_data=items)
        PurchaseService.receive(purchase)

        mv = StockMovement.objects.filter(
            product=product, movement_type=MovementType.IN,
            source_type="purchase", source_id=purchase.pk,
        ).first()
        assert mv is not None
        assert mv.quantity == Decimal("15")

    def test_receive_updates_product_prices(self):
        company = CompanyFactory()
        product = ProductFactory(cost_price=Decimal("1000"), sell_price=Decimal("1500"))
        items   = make_items([(product, Decimal("5"), Decimal("2000"), Decimal("3000"))])
        purchase = PurchaseService.create(company=company, items_data=items)
        PurchaseService.receive(purchase)

        product.refresh_from_db()
        assert product.cost_price == Decimal("2000")
        assert product.sell_price == Decimal("3000")

    def test_receive_changes_status(self):
        company  = CompanyFactory()
        product  = ProductFactory()
        items    = make_items([(product, Decimal("1"), Decimal("1000"), Decimal("1500"))])
        purchase = PurchaseService.create(company=company, items_data=items)
        PurchaseService.receive(purchase)

        purchase.refresh_from_db()
        assert purchase.status == PurchaseStatus.RECEIVED

    def test_receive_already_received_raises(self):
        company  = CompanyFactory()
        product  = ProductFactory()
        items    = make_items([(product, Decimal("5"), Decimal("1000"), Decimal("1500"))])
        purchase = PurchaseService.create(company=company, items_data=items)
        PurchaseService.receive(purchase)

        with pytest.raises(BusinessLogicError, match="Qoralama"):
            PurchaseService.receive(purchase)


@pytest.mark.django_db
class TestPurchasePay:

    def _make_received_purchase(self, amount=Decimal("100000")):
        company  = CompanyFactory()
        product  = ProductFactory()
        qty      = Decimal("10")
        cost     = amount / qty
        items    = make_items([(product, qty, cost, cost * Decimal("1.2"))])
        purchase = PurchaseService.create(company=company, items_data=items)
        PurchaseService.receive(purchase)
        purchase.refresh_from_db()
        return purchase

    def test_full_payment(self):
        purchase = self._make_received_purchase(Decimal("50000"))
        PurchaseService.pay(purchase, Decimal("50000"))
        purchase.refresh_from_db()
        assert purchase.status      == PurchaseStatus.PAID
        assert purchase.debt_amount == Decimal("0")

    def test_partial_payment(self):
        purchase = self._make_received_purchase(Decimal("100000"))
        PurchaseService.pay(purchase, Decimal("40000"))
        purchase.refresh_from_db()
        assert purchase.status      == PurchaseStatus.PARTIAL
        assert purchase.debt_amount == Decimal("60000")
        assert purchase.paid_amount == Decimal("40000")

    def test_multiple_payments(self):
        purchase = self._make_received_purchase(Decimal("100000"))
        PurchaseService.pay(purchase, Decimal("30000"))
        purchase.refresh_from_db()
        PurchaseService.pay(purchase, Decimal("70000"))
        purchase.refresh_from_db()
        assert purchase.status      == PurchaseStatus.PAID
        assert purchase.debt_amount == Decimal("0")

    def test_overpayment_raises(self):
        purchase = self._make_received_purchase(Decimal("50000"))
        with pytest.raises(BusinessLogicError, match="ko'p"):
            PurchaseService.pay(purchase, Decimal("99999"))

    def test_pay_draft_raises(self):
        company  = CompanyFactory()
        product  = ProductFactory()
        items    = make_items([(product, Decimal("1"), Decimal("1000"), Decimal("1500"))])
        purchase = PurchaseService.create(company=company, items_data=items)
        with pytest.raises(BusinessLogicError, match="Qoralama"):
            PurchaseService.pay(purchase, Decimal("1000"))

    def test_pay_already_paid_raises(self):
        purchase = self._make_received_purchase(Decimal("10000"))
        PurchaseService.pay(purchase, Decimal("10000"))
        purchase.refresh_from_db()
        with pytest.raises(BusinessLogicError, match="to'liq to'langan"):
            PurchaseService.pay(purchase, Decimal("1000"))

    def test_zero_payment_raises(self):
        purchase = self._make_received_purchase()
        with pytest.raises(BusinessLogicError):
            PurchaseService.pay(purchase, Decimal("0"))


@pytest.mark.django_db
class TestPurchaseCancel:

    def test_cancel_draft(self):
        company  = CompanyFactory()
        product  = ProductFactory()
        items    = make_items([(product, Decimal("5"), Decimal("1000"), Decimal("1500"))])
        purchase = PurchaseService.create(company=company, items_data=items)
        PurchaseService.cancel(purchase, reason="Test")
        purchase.refresh_from_db()
        assert purchase.status == PurchaseStatus.CANCELLED

    def test_cancel_received_returns_stock(self):
        """Qabul qilingan xarid bekor bo'lsa — stock qaytariladi."""
        company  = CompanyFactory()
        product  = ProductFactory()
        items    = make_items([(product, Decimal("10"), Decimal("1000"), Decimal("1500"))])
        purchase = PurchaseService.create(company=company, items_data=items)
        PurchaseService.receive(purchase)

        product.stock.refresh_from_db()
        assert product.stock.quantity == Decimal("10")

        PurchaseService.cancel(purchase, reason="Qaytarish")
        product.stock.refresh_from_db()
        assert product.stock.quantity == Decimal("0")

    def test_cancel_paid_raises(self):
        company  = CompanyFactory()
        product  = ProductFactory()
        items    = make_items([(product, Decimal("1"), Decimal("1000"), Decimal("1500"))])
        purchase = PurchaseService.create(company=company, items_data=items)
        PurchaseService.receive(purchase)
        purchase.refresh_from_db()
        PurchaseService.pay(purchase, purchase.total_amount)
        purchase.refresh_from_db()
        with pytest.raises(BusinessLogicError, match="bekor qilish mumkin emas"):
            PurchaseService.cancel(purchase)


@pytest.mark.django_db
class TestPurchaseQueries:

    def test_get_debts(self):
        company  = CompanyFactory()
        product  = ProductFactory()
        items    = make_items([(product, Decimal("1"), Decimal("1000"), Decimal("1500"))])
        purchase = PurchaseService.create(company=company, items_data=items)
        PurchaseService.receive(purchase)

        debt_ids = list(PurchaseService.get_debts().values_list("pk", flat=True))
        assert purchase.pk in debt_ids

    def test_get_overdue(self):
        from datetime import date, timedelta
        from purchases.models import Purchase, PurchaseStatus
        company  = CompanyFactory()
        product  = ProductFactory()
        items    = make_items([(product, Decimal("1"), Decimal("1000"), Decimal("1500"))])
        due      = date.today() - timedelta(days=1)
        purchase = PurchaseService.create(
            company=company, items_data=items, due_date=due,
        )
        PurchaseService.receive(purchase)

        p = Purchase.objects.get(pk=purchase.pk)
        assert p.status      == PurchaseStatus.RECEIVED
        assert p.debt_amount  > 0
        assert p.due_date    == due

        overdue_ids = list(PurchaseService.get_overdue().values_list("pk", flat=True))
        assert p.pk in overdue_ids
