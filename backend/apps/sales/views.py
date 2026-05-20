"""
Sales views.

CartViewSet   — Redis cart (add, scan, update, remove, clear)
SaleViewSet   — Sale CRUD + checkout + return
"""
from decimal import Decimal

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.mixins import SoftDeleteMixin
from core.permissions import IsAdminOrAbove, IsCashier

from .cart import CartService
from .filters import SaleFilter
from .models import Sale
from .serializers import (
    AddToCartSerializer,
    CartSerializer,
    CheckoutSerializer,
    ReturnSaleSerializer,
    SaleDetailSerializer,
    SaleListSerializer,
    ScanBarcodeSerializer,
    UpdateCartItemSerializer,
)
from .services import SaleService


# ─── Cart ViewSet ─────────────────────────────────────────────────────────────

@extend_schema(tags=["Cart"])
class CartViewSet(viewsets.ViewSet):
    """
    Redis Cart — POS sahifasi uchun.
    Har bir kassir o'z cartiga ega.
    """
    permission_classes = [IsCashier]

    @extend_schema(summary="Cartni ko'rish")
    @action(detail=False, methods=["get"])
    def cart(self, request):
        data = CartService.get_cart(request.user.pk)
        return Response({"success": True, "data": CartSerializer(data).data})

    @extend_schema(summary="Cartga mahsulot qo'shish", request=AddToCartSerializer)
    @action(detail=False, methods=["post"], url_path="add")
    def add(self, request):
        s = AddToCartSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = CartService.add_item(
            user_id    = request.user.pk,
            product_id = s.validated_data["product_id"],
            quantity   = s.validated_data["quantity"],
        )
        return Response({"success": True, "data": CartSerializer(data).data})

    @extend_schema(summary="Barcode / QR scan → cart", request=ScanBarcodeSerializer)
    @action(detail=False, methods=["post"], url_path="scan")
    def scan(self, request):
        """Scanner natijasi — barcode orqali mahsulot cartga qo'shiladi."""
        s = ScanBarcodeSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = CartService.add_by_barcode(
            user_id  = request.user.pk,
            barcode  = s.validated_data["barcode"],
            quantity = s.validated_data["quantity"],
        )
        return Response({"success": True, "data": CartSerializer(data).data})

    @extend_schema(summary="Cart itemni yangilash", request=UpdateCartItemSerializer)
    @action(detail=False, methods=["patch"], url_path="update/(?P<product_id>[0-9]+)")
    def update_item(self, request, product_id=None):
        s = UpdateCartItemSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        data = CartService.update_item(
            user_id    = request.user.pk,
            product_id = int(product_id),
            quantity   = s.validated_data["quantity"],
        )
        return Response({"success": True, "data": CartSerializer(data).data})

    @extend_schema(summary="Cart itemni o'chirish")
    @action(detail=False, methods=["delete"], url_path="remove/(?P<product_id>[0-9]+)")
    def remove_item(self, request, product_id=None):
        data = CartService.remove_item(
            user_id    = request.user.pk,
            product_id = int(product_id),
        )
        return Response({"success": True, "data": CartSerializer(data).data})

    @extend_schema(summary="Cartni tozalash")
    @action(detail=False, methods=["delete"], url_path="clear")
    def clear(self, request):
        CartService.clear(request.user.pk)
        return Response({"success": True, "message": "Cart tozalandi."})


# ─── Sale ViewSet ─────────────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(summary="Sotuvlar ro'yxati", tags=["Sales"]),
    retrieve=extend_schema(summary="Sotuv detail", tags=["Sales"]),
)
class SaleViewSet(SoftDeleteMixin, viewsets.ModelViewSet):
    """
    Sales — checkout va tarix.
    """
    filterset_class   = SaleFilter
    ordering_fields   = ["created_at", "net_amount"]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        return SaleService.get_queryset()

    def get_permissions(self):
        if self.action in ("return_sale", "daily_summary"):
            return [IsAdminOrAbove()]
        return [IsCashier()]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SaleDetailSerializer
        return SaleListSerializer

    @extend_schema(
        summary="Checkout — cartni yakunlash",
        tags=["Sales"],
        request=CheckoutSerializer,
    )
    @action(detail=False, methods=["post"], url_path="checkout")
    def checkout(self, request):
        """
        Asosiy sotuv action.
        Cart → Sale + StockDeduct + Payment.
        """
        s = CheckoutSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        sale = SaleService.checkout(
            user_id      = request.user.pk,
            payments     = [
                {"method": p["method"], "amount": p["amount"]}
                for p in s.validated_data["payments"]
            ],
            discount_pct = s.validated_data.get("discount_pct", Decimal("0")),
            note         = s.validated_data.get("note", ""),
            cashier      = request.user,
        )
        return Response(
            {
                "success": True,
                "message": f"Sotuv yakunlandi. Chek: {sale.invoice_no}",
                "data":    SaleDetailSerializer(sale).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Sotuvni qaytarish",
        tags=["Sales"],
        request=ReturnSaleSerializer,
    )
    @action(detail=True, methods=["post"], url_path="return",
            permission_classes=[IsAdminOrAbove])
    def return_sale(self, request, pk=None):
        """
        To'liq yoki qisman qaytarish.
        items bo'sh bo'lsa — to'liq qaytarish.
        """
        sale = self.get_object()
        s    = ReturnSaleSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        items_to_return = s.validated_data.get("items") or None
        if items_to_return == []:
            items_to_return = None  # bo'sh list → to'liq qaytarish

        updated = SaleService.return_sale(
            sale            = sale,
            items_to_return = items_to_return,
            reason          = s.validated_data.get("reason", ""),
            cashier         = request.user,
        )
        return Response({
            "success": True,
            "message": "Qaytarish muvaffaqiyatli amalga oshirildi.",
            "data":    SaleDetailSerializer(updated).data,
        })

    @extend_schema(summary="Kunlik sotuv statistikasi", tags=["Sales"])
    @action(detail=False, methods=["get"], url_path="daily-summary",
            permission_classes=[IsAdminOrAbove])
    def daily_summary(self, request):
        """?date=2024-01-15 yoki hozirgi kun."""
        from datetime import date
        date_str = request.query_params.get("date")
        if date_str:
            try:
                query_date = date.fromisoformat(date_str)
            except ValueError:
                return Response(
                    {"success": False, "error": {"message": "Noto'g'ri sana formati. YYYY-MM-DD."}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            query_date = None

        data = SaleService.get_daily_summary(query_date)
        return Response({"success": True, "data": data})
