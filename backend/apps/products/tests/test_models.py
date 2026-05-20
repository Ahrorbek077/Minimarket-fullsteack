"""
Products model testlari.
pytest -v apps/products/tests/test_models.py
"""
import pytest
from decimal import Decimal

from products.models import Category, Product, Unit
from .factories import (
    CategoryFactory, ProductFactory,
    SubCategoryFactory, UnitFactory, NoBarCodeProductFactory,
)


@pytest.mark.django_db
class TestCategoryModel:

    def test_create_root_category(self):
        cat = CategoryFactory(name="Oziq-ovqat")
        assert cat.pk is not None
        assert cat.name == "Oziq-ovqat"
        assert cat.parent is None
        assert cat.is_root is True

    def test_create_sub_category(self):
        parent = CategoryFactory(name="Ichimliklar")
        child  = SubCategoryFactory(name="Choy", parent=parent)
        assert child.parent == parent
        assert child.is_root is False

    def test_str_root(self):
        cat = CategoryFactory(name="Texnika")
        assert str(cat) == "Texnika"

    def test_str_sub(self):
        parent = CategoryFactory(name="Texnika")
        child  = SubCategoryFactory(name="Telefon", parent=parent)
        assert str(child) == "Texnika → Telefon"

    def test_get_ancestors_empty_for_root(self):
        cat = CategoryFactory()
        assert cat.get_ancestors() == []

    def test_get_ancestors(self):
        root   = CategoryFactory(name="A")
        mid    = SubCategoryFactory(name="B", parent=root)
        leaf   = SubCategoryFactory(name="C", parent=mid)
        ancestors = leaf.get_ancestors()
        assert ancestors == [root, mid]

    def test_soft_delete(self):
        cat = CategoryFactory()
        cat.delete()
        assert Category.objects.filter(pk=cat.pk).count() == 0
        assert Category.all_objects.filter(pk=cat.pk).count() == 1


@pytest.mark.django_db
class TestUnitModel:

    def test_create_unit(self):
        unit = UnitFactory(name="Kilogram", short_name="kg")
        assert unit.pk is not None
        assert str(unit) == "Kilogram (kg)"

    def test_soft_delete(self):
        unit = UnitFactory()
        unit.delete()
        assert Unit.objects.filter(pk=unit.pk).count() == 0


@pytest.mark.django_db
class TestProductModel:

    def test_create_product(self):
        product = ProductFactory(
            name="Lipton choy",
            cost_price=Decimal("8000.00"),
            sell_price=Decimal("10000.00"),
        )
        assert product.pk is not None
        assert product.name == "Lipton choy"
        assert product.is_active is True

    def test_profit_margin(self):
        product = ProductFactory(
            cost_price=Decimal("10000.00"),
            sell_price=Decimal("12000.00"),
        )
        assert product.profit_margin == 20.0

    def test_profit_margin_zero_cost(self):
        product = ProductFactory(cost_price=Decimal("0.00"))
        assert product.profit_margin == 0.0

    def test_profit_amount(self):
        product = ProductFactory(
            cost_price=Decimal("5000.00"),
            sell_price=Decimal("7000.00"),
        )
        assert product.profit_amount == Decimal("2000.00")

    def test_barcode_unique(self):
        ProductFactory(barcode="1234567890123")
        with pytest.raises(Exception):
            ProductFactory(barcode="1234567890123")

    def test_no_barcode_allowed(self):
        """Barcode ixtiyoriy."""
        p1 = NoBarCodeProductFactory()
        p2 = NoBarCodeProductFactory()
        assert p1.barcode is None
        assert p2.barcode is None

    def test_soft_delete(self):
        product = ProductFactory()
        product.delete()
        assert Product.objects.filter(pk=product.pk).count() == 0
        assert Product.all_objects.filter(pk=product.pk).count() == 1

    def test_str(self):
        product = ProductFactory(name="Coca-Cola 0.5L")
        assert str(product) == "Coca-Cola 0.5L"

    def test_default_is_active_true(self):
        product = ProductFactory()
        assert product.is_active is True
