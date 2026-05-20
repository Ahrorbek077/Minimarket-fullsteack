"""
Products factory classlar.
"""
import factory
from decimal import Decimal
from factory.django import DjangoModelFactory

from products.models import Category, Product, Unit


class UnitFactory(DjangoModelFactory):
    name       = factory.Sequence(lambda n: f"Unit {n}")
    short_name = factory.Sequence(lambda n: f"u{n}")

    class Meta:
        model = Unit
        django_get_or_create = ["name"]


class CategoryFactory(DjangoModelFactory):
    name  = factory.Sequence(lambda n: f"Category {n}")
    icon  = "📦"
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = Category


class SubCategoryFactory(CategoryFactory):
    """Ichki kategoriya."""
    name   = factory.Sequence(lambda n: f"SubCategory {n}")
    parent = factory.SubFactory(CategoryFactory)


class ProductFactory(DjangoModelFactory):
    name       = factory.Sequence(lambda n: f"Product {n}")
    barcode    = factory.Sequence(lambda n: f"123456789{n:04d}")
    category   = factory.SubFactory(CategoryFactory)
    unit       = factory.SubFactory(UnitFactory)
    cost_price = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    sell_price = factory.LazyAttribute(lambda o: o.cost_price * Decimal("1.2"))
    min_stock  = 5
    is_active  = True

    class Meta:
        model = Product


class InactiveProductFactory(ProductFactory):
    is_active = False


class NoBarCodeProductFactory(ProductFactory):
    barcode = None
