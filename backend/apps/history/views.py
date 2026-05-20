"""
History views — faqat o'qish.
Yozish signallar orqali avtomatik.
"""
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import viewsets

from core.permissions import IsAccountant, IsAdminOrAbove

from .filters import AuditLogFilter
from .models import AuditLog
from .serializers import AuditLogSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Audit tarixi ro'yxati",
        tags=["History"],
        parameters=[
            OpenApiParameter("action",    str, description="login|create|update|delete|sale_checkout..."),
            OpenApiParameter("model",     str, description="User|Product|Sale|Purchase"),
            OpenApiParameter("object_id", int, description="Obyekt ID"),
            OpenApiParameter("user",      int, description="Foydalanuvchi ID"),
            OpenApiParameter("date_from", str, description="2024-01-01"),
            OpenApiParameter("date_to",   str, description="2024-12-31"),
        ],
    ),
    retrieve=extend_schema(summary="Audit yozuvi detail", tags=["History"]),
)
class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Audit log — faqat o'qish.
    Admin+ va Buxgalter ko'ra oladi.
    POST/PUT/DELETE yo'q — tarixni o'zgartirish mumkin emas.
    """
    serializer_class   = AuditLogSerializer
    filterset_class    = AuditLogFilter
    search_fields      = ["object_repr", "user__full_name", "user__email"]
    ordering_fields    = ["created_at"]

    def get_queryset(self):
        return (
            AuditLog.objects
            .select_related("user")
            .order_by("-created_at")
        )

    def get_permissions(self):
        # Admin barini ko'radi, buxgalter ham ko'radi
        return [IsAccountant()]
