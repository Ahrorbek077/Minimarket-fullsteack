import factory
from factory.django import DjangoModelFactory
from decimal import Decimal

from inventory.models import Stock, StockMovement, MovementType
from products.tests.factories import ProductFactory
from users.tests.factories import UserFactory


class StockFactory(DjangoModelFactory):
    product  = factory.SubFactory(ProductFactory)
    quantity = Decimal("100.00")

    class Meta:
        model = Stock
        django_get_or_create = ["product"]

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        Signal Stock(qty=0) yaratadi — biz uni kerakli miqdorga yangilaymiz.
        """
        from inventory.models import Stock as StockModel
        product  = kwargs["product"]
        quantity = kwargs.get("quantity", Decimal("100.00"))
        stock, _ = StockModel.objects.get_or_create(
            product=product,
            defaults={"quantity": quantity},
        )
        if stock.quantity != quantity:
            stock.quantity = quantity
            stock.save(update_fields=["quantity"])
        return stock


class StockMovementFactory(DjangoModelFactory):
    product       = factory.SubFactory(ProductFactory)
    movement_type = MovementType.IN
    quantity      = Decimal("10.00")
    qty_before    = Decimal("0.00")
    qty_after     = Decimal("10.00")
    source_type   = "manual"
    created_by    = factory.SubFactory(UserFactory)

    class Meta:
        model = StockMovement
