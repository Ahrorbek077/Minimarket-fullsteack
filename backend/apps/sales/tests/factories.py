import factory
from decimal import Decimal
from factory.django import DjangoModelFactory

from products.tests.factories import ProductFactory
from users.tests.factories import UserFactory
from sales.models import PaymentMethod, Sale, SaleItem, SalePayment, SaleStatus


class SaleFactory(DjangoModelFactory):
    invoice_no      = factory.Sequence(lambda n: f"INV-20240101-{n:06d}")
    status          = SaleStatus.COMPLETED
    total_amount    = Decimal("50000.00")
    discount_pct    = Decimal("0.00")
    discount_amount = Decimal("0.00")
    net_amount      = Decimal("50000.00")
    paid_amount     = Decimal("50000.00")
    debt_amount     = Decimal("0.00")
    cashier         = factory.SubFactory(UserFactory)

    class Meta:
        model = Sale


class SaleItemFactory(DjangoModelFactory):
    sale                = factory.SubFactory(SaleFactory)
    product             = factory.SubFactory(ProductFactory)
    quantity            = Decimal("2.00")
    sell_price          = Decimal("5000.00")
    cost_price_snapshot = Decimal("3000.00")
    total               = Decimal("10000.00")

    class Meta:
        model = SaleItem


class SalePaymentFactory(DjangoModelFactory):
    sale   = factory.SubFactory(SaleFactory)
    method = PaymentMethod.CASH
    amount = Decimal("50000.00")

    class Meta:
        model = SalePayment
