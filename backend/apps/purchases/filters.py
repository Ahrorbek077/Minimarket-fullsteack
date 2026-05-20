import django_filters
from .models import Purchase, PurchaseStatus


class PurchaseFilter(django_filters.FilterSet):
    company   = django_filters.NumberFilter(field_name="company__id")
    status    = django_filters.ChoiceFilter(choices=PurchaseStatus.choices)
    date_from = django_filters.DateFilter(field_name="created_at", lookup_expr="date__gte")
    date_to   = django_filters.DateFilter(field_name="created_at", lookup_expr="date__lte")
    overdue   = django_filters.BooleanFilter(method="filter_overdue")

    class Meta:
        model  = Purchase
        fields = ["company", "status", "date_from", "date_to", "overdue"]

    def filter_overdue(self, queryset, name, value):
        from django.utils import timezone
        if value:
            return queryset.filter(
                due_date__lt=timezone.now().date(),
                debt_amount__gt=0,
            )
        return queryset
