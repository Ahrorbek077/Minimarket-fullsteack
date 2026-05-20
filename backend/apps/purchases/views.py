"""
Purchases views.
"""
from decimal import Decimal

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.mixins import SoftDeleteMixin
from core.permissions import IsAdminOrAbove, IsStorekeeper

from .filters import PurchaseFilter
from .models import Purchase
from .serializers import (
    PaySerializer,
    PurchaseCreateSerializer,
    PurchaseDetailSerializer,
    PurchaseListSerializer,
)
from .services import PurchaseService


@extend_schema_view(
    list=extend_schema(summary="Xaridlar ro'yxati", tags=["Purchases"]),
    retrieve=extend_schema(summary="Xarid detail", tags=["Purchases"]),
    create=extend_schema(summary="Yangi xarid yaratish", tags=["Purchases"]),
    destroy=extend_schema(summary="Xaridni o'chirish (soft)", tags=["Purchases"]),
)
class PurchaseViewSet(SoftDeleteMixin, viewsets.ModelViewSet):
    """
    Xaridlar CRUD.
    - Ko'rish: Storekeeper+
    - Yaratish/Boshqarish: Admin yoki Storekeeper
    """
    filterset_class = PurchaseFilter
    ordering_fields = ["created_at", "total_amount", "debt_amount"]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        return PurchaseService.get_queryset()

    def get_permissions(self):
        if self.action in ("list", "retrieve", "debts", "overdue"):
            return [IsStorekeeper()]
        return [IsAdminOrAbove()]

    def get_serializer_class(self):
        if self.action == "create":
            return PurchaseCreateSerializer
        if self.action == "retrieve":
            return PurchaseDetailSerializer
        return PurchaseListSerializer

    def create(self, request, *args, **kwargs):
        serializer = PurchaseCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        from companies.models import Branch, Company
        company = Company.objects.get(pk=data["company_id"])
        branch  = None
        if data.get("branch_id"):
            branch = Branch.objects.get(pk=data["branch_id"])

        purchase = PurchaseService.create(
            company    = company,
            branch     = branch,
            items_data = data["items"],
            invoice_no = data.get("invoice_no", ""),
            due_date   = data.get("due_date"),
            note       = data.get("note", ""),
            created_by = request.user,
        )
        return Response(
            {"success": True, "data": PurchaseDetailSerializer(purchase).data},
            status=status.HTTP_201_CREATED,
        )

    # ── Actions ───────────────────────────────────────────────────────────

    @extend_schema(summary="Xaridni qabul qilish → omborga tushirish", tags=["Purchases"])
    @action(detail=True, methods=["post"], url_path="receive")
    def receive(self, request, pk=None):
        """Draft → Received. Mahsulotlar omborga tushadi."""
        purchase = self.get_object()
        updated  = PurchaseService.receive(purchase, created_by=request.user)
        return Response({
            "success": True,
            "message": "Xarid qabul qilindi. Mahsulotlar omborga tushirildi.",
            "data":    PurchaseDetailSerializer(updated).data,
        })

    @extend_schema(summary="Qarz to'lash", tags=["Purchases"], request=PaySerializer)
    @action(detail=True, methods=["post"], url_path="pay")
    def pay(self, request, pk=None):
        """Qarz to'lash — qisman yoki to'liq."""
        purchase   = self.get_object()
        serializer = PaySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = PurchaseService.pay(
            purchase = purchase,
            amount   = Decimal(str(serializer.validated_data["amount"])),
            note     = serializer.validated_data.get("note", ""),
            paid_by  = request.user,
        )
        purchase.refresh_from_db()
        return Response({
            "success":     True,
            "message":     "To'lov qabul qilindi.",
            "payment":     {"id": payment.pk, "amount": str(payment.amount)},
            "debt_amount": str(purchase.debt_amount),
            "status":      purchase.status,
        })

    @extend_schema(summary="Xaridni bekor qilish", tags=["Purchases"])
    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        """Xaridni bekor qilish. Received bo'lsa stock qaytariladi."""
        purchase = self.get_object()
        reason   = request.data.get("reason", "")
        updated  = PurchaseService.cancel(purchase, reason=reason, created_by=request.user)
        return Response({
            "success": True,
            "message": "Xarid bekor qilindi.",
            "status":  updated.status,
        })

    @extend_schema(summary="Qarzli xaridlar", tags=["Purchases"])
    @action(detail=False, methods=["get"], url_path="debts")
    def debts(self, request):
        """To'lanmagan barcha xaridlar."""
        qs         = PurchaseService.get_debts()
        serializer = PurchaseListSerializer(qs, many=True)
        return Response({"success": True, "count": qs.count(), "data": serializer.data})

    @extend_schema(summary="Muddati o'tgan qarzlar", tags=["Purchases"])
    @action(detail=False, methods=["get"], url_path="overdue")
    def overdue(self, request):
        """Due date o'tib ketgan qarzlar."""
        qs         = PurchaseService.get_overdue()
        serializer = PurchaseListSerializer(qs, many=True)
        return Response({"success": True, "count": qs.count(), "data": serializer.data})
