"""
Reports test helpers — sotuv va xarid ma'lumotlari yaratish.
"""
from decimal import Decimal
from datetime import date, timedelta

from inventory.tests.factories import StockFactory
from products.tests.factories import ProductFactory
from sales.cart import CartService
from sales.models import PaymentMethod
from sales.services import SaleService
from users.tests.factories import UserFactory


def make_sale(cashier=None, amount=Decimal("10000"), method=PaymentMethod.CASH):
    """Test uchun sotuv yaratish."""
    if cashier is None:
        cashier = UserFactory()
    product = ProductFactory(sell_price=amount)
    StockFactory(product=product, quantity=Decimal("50"))
    CartService.add_item(cashier.pk, product.pk, Decimal("1"))
    sale = SaleService.checkout(
        user_id  = cashier.pk,
        payments = [{"method": method, "amount": str(amount)}],
        cashier  = cashier,
    )
    CartService.clear(cashier.pk)
    return sale


def make_purchase(amount=Decimal("50000")):
    """Test uchun xarid yaratish."""
    from companies.tests.factories import CompanyFactory
    from purchases.services import PurchaseService
    company = CompanyFactory()
    product = ProductFactory()
    StockFactory(product=product, quantity=Decimal("0"))
    purchase = PurchaseService.create(
        company    = company,
        items_data = [{"product": product, "quantity": Decimal("10"),
                       "cost_price": amount / 10, "sell_price": amount / 10 * Decimal("1.3")}],
    )
    return purchase
