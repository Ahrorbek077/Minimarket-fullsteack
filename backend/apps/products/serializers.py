"""
Products serializers.
"""
from rest_framework import serializers

from .models import Category, Product, Unit


# ─── Unit ─────────────────────────────────────────────────────────────────────

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Unit
        fields = ["id", "name", "short_name", "created_at"]
        read_only_fields = ["id", "created_at"]


# ─── Category ─────────────────────────────────────────────────────────────────

class CategoryShortSerializer(serializers.ModelSerializer):
    """Qisqa — product ichida ishlatiladigan."""
    class Meta:
        model  = Category
        fields = ["id", "name", "icon"]


class CategorySerializer(serializers.ModelSerializer):
    """To'liq — children bilan."""
    children      = CategoryShortSerializer(many=True, read_only=True)
    parent_name   = serializers.CharField(
        source="parent.name", read_only=True, default=None
    )
    product_count = serializers.SerializerMethodField()

    class Meta:
        model  = Category
        fields = [
            "id", "name", "icon", "order",
            "parent", "parent_name", "children",
            "product_count", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_product_count(self, obj) -> int:
        return obj.products.filter(deleted_at__isnull=True, is_active=True).count()


class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = ["name", "icon", "order", "parent"]


# ─── Product ──────────────────────────────────────────────────────────────────

class ProductListSerializer(serializers.ModelSerializer):
    """Ro'yxat uchun — qisqa."""
    category_name = serializers.CharField(
        source="category.name", read_only=True, default=None
    )
    unit_short    = serializers.CharField(
        source="unit.short_name", read_only=True, default=None
    )
    stock_qty     = serializers.SerializerMethodField()
    is_low_stock  = serializers.SerializerMethodField()

    class Meta:
        model  = Product
        fields = [
            "id", "name", "barcode",
            "category_name", "unit_short",
            "cost_price", "sell_price", "profit_margin",
            "stock_qty", "is_low_stock",
            "is_active", "image",
        ]

    def get_stock_qty(self, obj):
        # Stock app qo'shilgach to'ldiriladi
        stock = getattr(obj, "_prefetched_stock", None)
        if hasattr(obj, "stock"):
            try:
                return float(obj.stock.quantity)
            except Exception:
                return 0.0
        return 0.0

    def get_is_low_stock(self, obj):
        try:
            return float(obj.stock.quantity) <= float(obj.min_stock)
        except Exception:
            return False


class ProductDetailSerializer(serializers.ModelSerializer):
    """To'liq — barcha ma'lumotlar."""
    category      = CategoryShortSerializer(read_only=True)
    category_id   = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(deleted_at__isnull=True),
        source="category", write_only=True, required=False, allow_null=True
    )
    unit          = UnitSerializer(read_only=True)
    unit_id       = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.filter(deleted_at__isnull=True),
        source="unit", write_only=True, required=False, allow_null=True
    )
    profit_margin = serializers.FloatField(read_only=True)
    profit_amount = serializers.DecimalField(
        max_digits=14, decimal_places=2, read_only=True
    )

    class Meta:
        model  = Product
        fields = [
            "id", "name", "barcode", "description",
            "category", "category_id",
            "unit", "unit_id",
            "cost_price", "sell_price",
            "profit_margin", "profit_amount",
            "min_stock", "is_active", "image",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProductCreateSerializer(serializers.ModelSerializer):
    """Yaratish uchun."""
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(deleted_at__isnull=True),
        source="category", required=False, allow_null=True
    )
    unit_id = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.filter(deleted_at__isnull=True),
        source="unit", required=False, allow_null=True
    )

    class Meta:
        model  = Product
        fields = [
            "name", "barcode", "description",
            "category_id", "unit_id",
            "cost_price", "sell_price",
            "min_stock", "is_active", "image",
        ]

    def validate_barcode(self, value):
        """Barcode unique bo'lishi kerak (yangilashda o'zini hisobga olmaslik)."""
        if value:
            qs = Product.objects.filter(
                barcode=value, deleted_at__isnull=True
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "Bu barcode allaqachon mavjud."
                )
        return value

    def validate(self, attrs):
        sell = attrs.get("sell_price", 0)
        cost = attrs.get("cost_price", 0)
        if sell and cost and sell < cost:
            raise serializers.ValidationError(
                {"sell_price": "Sotish narxi tan narxidan kam bo'lmasligi kerak."}
            )
        return attrs


class ProductUpdateSerializer(ProductCreateSerializer):
    """Yangilash — name majburiy emas."""
    name = serializers.CharField(required=False)


class ProductBarcodeSerializer(serializers.ModelSerializer):
    """Barcode scan — POS uchun tez javob."""
    category_name = serializers.CharField(source="category.name", default=None)
    unit_short    = serializers.CharField(source="unit.short_name", default=None)
    stock_qty     = serializers.SerializerMethodField()

    class Meta:
        model  = Product
        fields = [
            "id", "name", "barcode",
            "category_name", "unit_short",
            "sell_price", "stock_qty", "image",
        ]

    def get_stock_qty(self, obj):
        try:
            return float(obj.stock.quantity)
        except Exception:
            return 0.0
