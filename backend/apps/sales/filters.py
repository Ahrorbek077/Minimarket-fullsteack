import django_filters
from .models import Sale, SaleStatus


class SaleFilter(django_filters.FilterSet):
    status    = django_filters.ChoiceFilter(choices=SaleStatus.choices)
    cashier   = django_filters.NumberFilter(field_name="cashier__id")
    date_from = django_filters.DateFilter(field_name="created_at", lookup_expr="date__gte")
    date_to   = django_filters.DateFilter(field_name="created_at", lookup_expr="date__lte")
    has_debt  = django_filters.BooleanFilter(method="filter_has_debt")

    class Meta:
        model  = Sale
        fields = ["status", "cashier", "date_from", "date_to", "has_debt"]

    def filter_has_debt(self, queryset, name, value):
        if value:
            return queryset.filter(debt_amount__gt=0)
        return queryset.filter(debt_amount=0)
