import factory
from decimal import Decimal
from factory.django import DjangoModelFactory

from companies.tests.factories import BranchFactory, CompanyFactory
from products.tests.factories import ProductFactory
from users.tests.factories import UserFactory
from purchases.models import Purchase, PurchaseItem, PurchasePayment, PurchaseStatus


class PurchaseFactory(DjangoModelFactory):
    company      = factory.SubFactory(CompanyFactory)
    branch       = factory.SubFactory(BranchFactory)
    status       = PurchaseStatus.DRAFT
    total_amount = Decimal("100000.00")
    paid_amount  = Decimal("0.00")
    debt_amount  = Decimal("100000.00")
    created_by   = factory.SubFactory(UserFactory)

    class Meta:
        model = Purchase


class ReceivedPurchaseFactory(PurchaseFactory):
    status = PurchaseStatus.RECEIVED


class PurchaseItemFactory(DjangoModelFactory):
    purchase   = factory.SubFactory(PurchaseFactory)
    product    = factory.SubFactory(ProductFactory)
    quantity   = Decimal("10.00")
    cost_price = Decimal("5000.00")
    sell_price = Decimal("7000.00")
    total      = Decimal("50000.00")

    class Meta:
        model = PurchaseItem


class PurchasePaymentFactory(DjangoModelFactory):
    purchase = factory.SubFactory(ReceivedPurchaseFactory)
    amount   = Decimal("50000.00")
    paid_by  = factory.SubFactory(UserFactory)

    class Meta:
        model = PurchasePayment
