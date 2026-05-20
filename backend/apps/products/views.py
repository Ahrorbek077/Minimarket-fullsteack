"""
Products views — faqat HTTP handling.
Logika services.py da.
"""
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.response import Response

from core.mixins import SoftDeleteMixin
from core.permissions import IsAdminOrAbove, IsCashier, IsStorekeeper

from .filters import ProductFilter
from .models import Category, Product, Unit
from .serializers import (
    CategoryCreateSerializer,
    CategorySerializer,
    ProductBarcodeSerializer,
    ProductCreateSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    ProductUpdateSerializer,
    UnitSerializer,
)
from .services import CategoryService, ProductService, UnitService


# ─── Unit ViewSet ──────────────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(summary="O'lchov birliklari ro'yxati", tags=["Units"]),
    create=extend_schema(summary="O'lchov birligi qo'shish", tags=["Units"]),
    update=extend_schema(summary="O'lchov birligini yangilash", tags=["Units"]),
    destroy=extend_schema(summary="O'lchov birligini o'chirish", tags=["Units"]),
)
class UnitViewSet(SoftDeleteMixin, viewsets.ModelViewSet):
    """O'lchov birliklari — Admin+ boshqaradi."""
    serializer_class   = UnitSerializer
    permission_classes = [IsAdminOrAbove]
    http_method_names  = ["get", "post", "put", "patch", "delete"]

    def get_queryset(self):
        return UnitService.get_all()


# ─── Category ViewSet ──────────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(summary="Kategoriyalar ro'yxati", tags=["Categories"]),
    create=extend_schema(summary="Kategoriya qo'shish", tags=["Categories"]),
    retrieve=extend_schema(summary="Kategoriya detail", tags=["Categories"]),
    update=extend_schema(summary="Kategoriyani yangilash", tags=["Categories"]),
    destroy=extend_schema(summary="Kategoriyani o'chirish", tags=["Categories"]),
)
class CategoryViewSet(SoftDeleteMixin, viewsets.ModelViewSet):
    """Kategoriyalar CRUD — Admin+ boshqaradi."""
    permission_classes = [IsAdminOrAbove]

    def get_queryset(self):
        return Category.objects.filter(
            deleted_at__isnull=True
        ).select_related("parent").prefetch_related("children").order_by("order", "name")

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return CategoryCreateSerializer
        return CategorySerializer

    @extend_schema(summary="Daraxtsimон kategoriyalar", tags=["Categories"])
    @action(detail=False, methods=["get"], url_path="tree")
    def tree(self, request):
        """Faqat root kategoriyalar + ichki bolalari bilan."""
        qs = CategoryService.get_tree()
        serializer = CategorySerializer(qs, many=True)
        return Response({"success": True, "data": serializer.data})


# ─── Product ViewSet ───────────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(
        summary="Mahsulotlar ro'yxati",
        tags=["Products"],
        parameters=[
            OpenApiParameter("name", str, description="Nom bo'yicha qidirish"),
            OpenApiParameter("barcode", str, description="Barcode bo'yicha"),
            OpenApiParameter("category_id", int, description="Kategoriya ID"),
            OpenApiParameter("is_active", bool, description="Faqat faol"),
            OpenApiParameter("low_stock", bool, description="Kam qoldiqlar"),
            OpenApiParameter("min_price", float, description="Minimal narx"),
            OpenApiParameter("max_price", float, description="Maksimal narx"),
        ],
    ),
    create=extend_schema(summary="Mahsulot qo'shish", tags=["Products"]),
    retrieve=extend_schema(summary="Mahsulot detail", tags=["Products"]),
    update=extend_schema(summary="Mahsulotni yangilash", tags=["Products"]),
    partial_update=extend_schema(summary="Mahsulotni qisman yangilash", tags=["Products"]),
    destroy=extend_schema(summary="Mahsulotni o'chirish (soft)", tags=["Products"]),
)
class ProductViewSet(SoftDeleteMixin, viewsets.ModelViewSet):
    """
    Mahsulotlar CRUD.
    - Ko'rish: Kassir+
    - Yaratish/Tahrirlash/O'chirish: Admin+ yoki Omborchi
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filterset_class = ProductFilter
    search_fields  = ["name", "barcode", "description"]
    ordering_fields = ["name", "sell_price", "cost_price", "created_at"]

    def get_queryset(self):
        return ProductService.get_queryset()

    def get_serializer_class(self):
        if self.action == "create":
            return ProductCreateSerializer
        if self.action in ("update", "partial_update"):
            return ProductUpdateSerializer
        if self.action == "retrieve":
            return ProductDetailSerializer
        if self.action == "by_barcode":
            return ProductBarcodeSerializer
        return ProductListSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve", "by_barcode"):
            return [IsCashier()]
        return [IsStorekeeper()]

    def perform_create(self, serializer):
        product = serializer.save()
        # Inventory app qo'shilgach stock avtomatik yaratiladi (signal orqali)

    def perform_destroy(self, instance):
        instance.delete()  # soft delete (BaseModel)

    # ── Custom actions ─────────────────────────────────────────────────────

    @extend_schema(
        summary="Barcode / QR kod bilan mahsulot topish",
        tags=["Products"],
        parameters=[
            OpenApiParameter("barcode", str, location="path", description="Barcode yoki QR")
        ],
    )
    @action(
        detail=False, methods=["get"],
        url_path="barcode/(?P<barcode>[^/.]+)",
        permission_classes=[IsCashier],
    )
    def by_barcode(self, request, barcode: str = None):
        """
        Barcode scanner natijasi.
        POS sahifasida mahsulotni cartga qo'shish uchun.
        """
        product = ProductService.get_by_barcode(barcode)
        serializer = self.get_serializer(product)
        return Response({"success": True, "data": serializer.data})

    @extend_schema(
        summary="Narxlarni yangilash",
        tags=["Products"],
        request={"application/json": {
            "type": "object",
            "properties": {
                "cost_price": {"type": "number"},
                "sell_price": {"type": "number"},
            }
        }},
    )
    @action(
        detail=True, methods=["patch"],
        url_path="update-price",
        permission_classes=[IsStorekeeper],
    )
    def update_price(self, request, pk=None):
        """Mahsulot narxini alohida yangilash."""
        product    = self.get_object()
        cost_price = request.data.get("cost_price")
        sell_price = request.data.get("sell_price")

        if cost_price is None and sell_price is None:
            return Response(
                {"success": False, "error": {"message": "cost_price yoki sell_price kerak."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated = ProductService.update_prices(
            product,
            cost_price=cost_price,
            sell_price=sell_price,
        )
        return Response({
            "success": True,
            "message": "Narx yangilandi.",
            "data": ProductDetailSerializer(updated).data,
        })

    @extend_schema(summary="Kam qoldiqli mahsulotlar", tags=["Products"])
    @action(
        detail=False, methods=["get"],
        url_path="low-stock",
        permission_classes=[IsStorekeeper],
    )
    def low_stock(self, request):
        """Minimum qoldiqdan past mahsulotlar ro'yxati."""
        products   = ProductService.get_low_stock_products()
        serializer = ProductListSerializer(products, many=True)
        return Response({
            "success": True,
            "count": products.count(),
            "data": serializer.data,
        })
