"""
Inventory views — faqat HTTP handling.
"""
from decimal import Decimal

from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import IsAdminOrAbove, IsStorekeeper

from .filters import StockMovementFilter
from .models import Stock, StockMovement
from .serializers import (
    StockAdjustSerializer,
    StockMovementSerializer,
    StockSerializer,
)
from .services import StockService


# ─── Stock ViewSet ─────────────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(summary="Barcha mahsulot qoldiqlari", tags=["Inventory"]),
    retrieve=extend_schema(summary="Mahsulot qoldig'i", tags=["Inventory"]),
)
class StockViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Qoldiqlarni ko'rish (faqat o'qish).
    Qo'shish/chiqarish faqat Purchase va Sale orqali bo'ladi.
    Manual tuzatish — adjust/ action orqali.
    """
    serializer_class   = StockSerializer
    permission_classes = [IsStorekeeper]
    search_fields      = ["product__name", "product__barcode"]
    ordering_fields    = ["quantity", "product__name", "updated_at"]

    def get_queryset(self):
        qs = (
            Stock.objects
            .select_related("product", "product__unit", "product__category")
            .filter(product__deleted_at__isnull=True)
            .order_by("product__name")
        )
        params = self.request.query_params
        if params.get("low_stock") in ("true", "1"):
            from django.db.models import F
            qs = qs.filter(quantity__lte=F("product__min_stock"), quantity__gt=0)
        if params.get("out_stock") in ("true", "1"):
            qs = qs.filter(quantity__lte=0)
        if params.get("search"):
            q = params.get("search")
            from django.db.models import Q
            qs = qs.filter(
                Q(product__name__icontains=q) | Q(product__barcode__icontains=q)
            )
        return qs

    @extend_schema(summary="Kam qoldiqlar", tags=["Inventory"])
    @action(detail=False, methods=["get"], url_path="low-stock")
    def low_stock(self, request):
        qs         = StockService.get_low_stock()
        serializer = StockSerializer(qs, many=True)
        return Response({
            "success": True,
            "count":   qs.count(),
            "data":    serializer.data,
        })

    @extend_schema(
        summary="Ombor umumiy statistikasi",
        tags=["Inventory"],
    )
    @action(
        detail=False, methods=["get"], url_path="summary",
        permission_classes=[IsAdminOrAbove],
    )
    def summary(self, request):
        data = StockService.get_stock_summary()
        return Response({"success": True, "data": data})

    @extend_schema(
        summary="Stock manual tuzatish",
        tags=["Inventory"],
        request=StockAdjustSerializer,
    )
    @action(
        detail=True, methods=["post"], url_path="adjust",
        permission_classes=[IsAdminOrAbove],
    )
    def adjust(self, request, pk=None):
        """
        Haqiqiy sanashdan keyin qoldiqni to'g'irlash.
        Faqat Admin+ bajara oladi — har bir tuzatish logga tushadi.
        """
        stock      = self.get_object()
        serializer = StockAdjustSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        movement = StockService.adjust(
            product      = stock.product,
            new_quantity = Decimal(str(serializer.validated_data["new_quantity"])),
            reason       = serializer.validated_data.get("reason", ""),
            created_by   = request.user,
        )
        stock.refresh_from_db()
        return Response({
            "success":   True,
            "message":   "Qoldiq tuzatildi.",
            "stock":     StockSerializer(stock).data,
            "movement":  StockMovementSerializer(movement).data,
        })


# ─── StockMovement ViewSet ─────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(
        summary="Ombor harakatlari tarixi",
        tags=["Inventory"],
        parameters=[
            OpenApiParameter("product",   int, description="Mahsulot ID"),
            OpenApiParameter("type",      str, description="in|out|return_in|return_out|adjust"),
            OpenApiParameter("source",    str, description="purchase|sale|manual"),
            OpenApiParameter("date_from", str, description="2024-01-01"),
            OpenApiParameter("date_to",   str, description="2024-12-31"),
        ],
    ),
    retrieve=extend_schema(summary="Harakat detail", tags=["Inventory"]),
)
class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Ombor harakatlari — faqat o'qish (create yo'q, avtomatik yoziladi).
    """
    serializer_class   = StockMovementSerializer
    permission_classes = [IsStorekeeper]
    filterset_class    = StockMovementFilter
    ordering_fields    = ["created_at", "quantity"]

    def get_queryset(self):
        return StockService.get_movements()
