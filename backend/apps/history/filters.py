import django_filters
from .models import AuditAction, AuditLog


class AuditLogFilter(django_filters.FilterSet):
    action     = django_filters.ChoiceFilter(choices=AuditAction.choices)
    model      = django_filters.CharFilter(field_name="model_name", lookup_expr="iexact")
    object_id  = django_filters.NumberFilter(field_name="object_id")
    user       = django_filters.NumberFilter(field_name="user__id")
    date_from  = django_filters.DateFilter(field_name="created_at", lookup_expr="date__gte")
    date_to    = django_filters.DateFilter(field_name="created_at", lookup_expr="date__lte")

    class Meta:
        model  = AuditLog
        fields = ["action", "model", "object_id", "user", "date_from", "date_to"]
