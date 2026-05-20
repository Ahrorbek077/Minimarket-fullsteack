import django_filters
from .models import StockMovement, MovementType


class StockMovementFilter(django_filters.FilterSet):
    product    = django_filters.NumberFilter(field_name="product__id")
    type       = django_filters.ChoiceFilter(
        field_name="movement_type", choices=MovementType.choices
    )
    source     = django_filters.CharFilter(field_name="source_type")
    date_from  = django_filters.DateFilter(field_name="created_at", lookup_expr="date__gte")
    date_to    = django_filters.DateFilter(field_name="created_at", lookup_expr="date__lte")

    class Meta:
        model  = StockMovement
        fields = ["product", "type", "source", "date_from", "date_to"]
