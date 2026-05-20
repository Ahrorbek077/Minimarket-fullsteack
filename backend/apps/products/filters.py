"""
Django-filter classlar — product filtrlash.
"""
import django_filters

from .models import Product, Category


class ProductFilter(django_filters.FilterSet):
    """
    Mahsulotlar uchun filter.
    GET /api/v1/products/products/?category=1&min_price=5000&search=lipton
    """
    name        = django_filters.CharFilter(lookup_expr="icontains")
    barcode     = django_filters.CharFilter(lookup_expr="exact")
    category    = django_filters.ModelChoiceFilter(
        queryset=Category.objects.filter(deleted_at__isnull=True)
    )
    category_id = django_filters.NumberFilter(field_name="category__id")
    min_price   = django_filters.NumberFilter(
        field_name="sell_price", lookup_expr="gte"
    )
    max_price   = django_filters.NumberFilter(
        field_name="sell_price", lookup_expr="lte"
    )
    is_active   = django_filters.BooleanFilter()
    low_stock   = django_filters.BooleanFilter(method="filter_low_stock")

    class Meta:
        model  = Product
        fields = [
            "name", "barcode", "category",
            "category_id", "is_active",
            "min_price", "max_price", "low_stock",
        ]

    def filter_low_stock(self, queryset, name, value):
        from django.db.models import F
        if value:
            return queryset.filter(stock__quantity__lte=F("min_stock"))
        return queryset
