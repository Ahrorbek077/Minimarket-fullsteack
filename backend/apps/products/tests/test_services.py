"""
Products services testlari.
pytest -v apps/products/tests/test_services.py
"""
import pytest
from decimal import Decimal

from core.exceptions import BusinessLogicError
from products.models import Product
from products.services import CategoryService, ProductService, UnitService
from .factories import CategoryFactory, ProductFactory, UnitFactory


@pytest.mark.django_db
class TestProductService:

    def test_get_by_barcode_success(self):
        product = ProductFactory(barcode="1234567890000", is_active=True)
        result  = ProductService.get_by_barcode("1234567890000")
        assert result == product

    def test_get_by_barcode_not_found(self):
        with pytest.raises(BusinessLogicError) as exc:
            ProductService.get_by_barcode("0000000000")
        assert exc.value.default_code == "product_not_found"

    def test_get_by_barcode_inactive_raises(self):
        ProductFactory(barcode="inactive001", is_active=False)
        with pytest.raises(BusinessLogicError):
            ProductService.get_by_barcode("inactive001")

    def test_create_product(self):
        cat  = CategoryFactory()
        unit = UnitFactory()
        product = ProductService.create({
            "name":       "Test mahsulot",
            "cost_price": Decimal("3000"),
            "sell_price": Decimal("4000"),
            "category":   cat,
            "unit":       unit,
        })
        assert product.pk is not None
        assert product.name == "Test mahsulot"

    def test_update_prices(self):
        product = ProductFactory(
            cost_price=Decimal("5000"),
            sell_price=Decimal("6000"),
        )
        updated = ProductService.update_prices(
            product,
            cost_price=Decimal("7000"),
            sell_price=Decimal("9000"),
        )
        assert updated.cost_price == Decimal("7000")
        assert updated.sell_price == Decimal("9000")

    def test_get_active_excludes_deleted(self):
        active  = ProductFactory()
        deleted = ProductFactory()
        deleted.delete()
        qs = ProductService.get_active()
        assert active in qs
        assert deleted not in qs

    def test_get_active_excludes_inactive(self):
        active   = ProductFactory(is_active=True)
        inactive = ProductFactory(is_active=False)
        qs = ProductService.get_active()
        assert active in qs
        assert inactive not in qs


@pytest.mark.django_db
class TestCategoryService:

    def test_get_tree_only_roots(self):
        root  = CategoryFactory()
        child = CategoryFactory(parent=root)
        tree  = list(CategoryService.get_tree())
        assert root in tree
        assert child not in tree

    def test_create_category(self):
        cat = CategoryService.create(name="Yangi kat")
        assert cat.pk is not None

    def test_create_subcategory(self):
        parent = CategoryFactory()
        child  = CategoryService.create(name="Child", parent_id=parent.pk)
        assert child.parent == parent

    def test_create_with_invalid_parent_raises(self):
        with pytest.raises(BusinessLogicError) as exc:
            CategoryService.create(name="X", parent_id=99999)
        assert exc.value.default_code == "not_found"
