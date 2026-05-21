"""
Companies views.
"""
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.mixins import SoftDeleteMixin
from core.permissions import IsAdminOrAbove

from .models import Branch, Company
from .serializers import (
    BranchCreateSerializer,
    BranchSerializer,
    CompanyCreateSerializer,
    CompanyDetailSerializer,
    CompanyListSerializer,
)
from .services import BranchService, CompanyService


@extend_schema_view(
    list=extend_schema(summary="Kompaniyalar ro'yxati", tags=["Companies"]),
    create=extend_schema(summary="Kompaniya qo'shish", tags=["Companies"]),
    retrieve=extend_schema(summary="Kompaniya detail (filiallar bilan)", tags=["Companies"]),
    update=extend_schema(summary="Kompaniyani yangilash", tags=["Companies"]),
    destroy=extend_schema(summary="Kompaniyani o'chirish", tags=["Companies"]),
)
class CompanyViewSet(SoftDeleteMixin, viewsets.ModelViewSet):
    """
    Kompaniyalar CRUD + filiallarni boshqarish.
    Faqat Admin+.
    """
    permission_classes = [IsAdminOrAbove]

    def get_queryset(self):
        search = self.request.query_params.get("search")
        return CompanyService.get_queryset(search=search)

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return CompanyCreateSerializer
        if self.action == "retrieve":
            return CompanyDetailSerializer
        return CompanyListSerializer

    def perform_create(self, serializer):
        CompanyService.create(serializer.validated_data)

    def perform_update(self, serializer):
        CompanyService.update(self.get_object(), serializer.validated_data)

    def perform_destroy(self, instance):
        CompanyService.soft_delete(instance)

    # ── Branch nested actions ──────────────────────────────────────────────

    @extend_schema(summary="Filiallar ro'yxati", tags=["Companies"])
    @action(detail=True, methods=["get", "post"], url_path="branches")
    def branches(self, request, pk=None):
        company = self.get_object()
        if request.method == "GET":
            branches = BranchService.get_for_company(company)
            return Response({
                "success": True,
                "results": BranchSerializer(branches, many=True).data,
                "data": BranchSerializer(branches, many=True).data,
            })
        # POST
        return self.add_branch_handler(request, company)

    def add_branch_handler(self, request, company):
        company    = self.get_object()
        serializer = BranchCreateSerializer(
            data=request.data,
            context={"request": request, "company": company},
        )
        serializer.is_valid(raise_exception=True)
        branch = BranchService.create(company, serializer.validated_data)
        return Response(
            {"success": True, "message": "Filial qo'shildi.", "data": BranchSerializer(branch).data},
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(summary="Filialni yangilash", tags=["Companies"])
    @action(detail=True, methods=["patch"], url_path="branches/(?P<branch_id>[0-9]+)/update")
    def update_branch(self, request, pk=None, branch_id=None):
        company    = self.get_object()
        branch     = BranchService.get_by_id(branch_id, company=company)
        serializer = BranchCreateSerializer(
            branch, data=request.data, partial=True,
            context={"request": request, "company": company},
        )
        serializer.is_valid(raise_exception=True)
        updated = BranchService.update(branch, serializer.validated_data)
        return Response({"success": True, "data": BranchSerializer(updated).data})

    @extend_schema(summary="Filialni o'chirish", tags=["Companies"])
    @action(
        detail=True, methods=["delete"],
        url_path="branches/(?P<branch_id>[0-9]+)/delete",
    )
    def delete_branch(self, request, pk=None, branch_id=None):
        company = self.get_object()
        branch  = BranchService.get_by_id(branch_id, company=company)
        branch.delete()
        return Response({"success": True, "message": "Filial o'chirildi."})

    @extend_schema(summary="Filial orqali xarid qilingan mahsulotlar", tags=["Companies"])
    @action(detail=True, methods=["get"], url_path="branches/(?P<branch_id>[0-9]+)/products")
    def branch_products(self, request, pk=None, branch_id=None):
        """Branch ga tegishli xaridlardan mahsulotlar ro'yxati."""
        from django.db.models import Sum, DecimalField, ExpressionWrapper, F
        from purchases.models import Purchase, PurchaseStatus
        from products.serializers import ProductListSerializer

        company = self.get_object()
        try:
            branch = company.branches.get(pk=branch_id, deleted_at__isnull=True)
        except Exception:
            return Response({"success": False, "error": {"message": "Filial topilmadi."}}, status=404)

        # Bu filialdan qilingan received xaridlardagi mahsulotlar
        from products.models import Product
        product_ids = (
            Purchase.objects
            .filter(branch=branch, status__in=[PurchaseStatus.RECEIVED, PurchaseStatus.PARTIAL, PurchaseStatus.PAID], deleted_at__isnull=True)
            .values_list("items__product_id", flat=True)
            .distinct()
        )
        products = Product.objects.filter(id__in=product_ids, deleted_at__isnull=True).select_related("category", "unit")
        serializer = ProductListSerializer(products, many=True)
        return Response({"success": True, "count": products.count(), "results": serializer.data})


