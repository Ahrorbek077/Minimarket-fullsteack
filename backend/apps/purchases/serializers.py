"""
Purchases serializers.
"""
from decimal import Decimal
from rest_framework import serializers

from products.models import Product
from .models import Purchase, PurchaseItem, PurchasePayment, PurchaseStatus


# ─── PurchaseItem ─────────────────────────────────────────────────────────────

class PurchaseItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    unit_short   = serializers.CharField(
        source="product.unit.short_name", read_only=True, default=None
    )

    class Meta:
        model  = PurchaseItem
        fields = [
            "id", "product", "product_name", "unit_short",
            "quantity", "cost_price", "sell_price", "total",
        ]
        read_only_fields = ["id", "total"]


class PurchaseItemCreateSerializer(serializers.Serializer):
    """Xarid yaratishda har bir qator uchun."""
    product_id  = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(deleted_at__isnull=True, is_active=True),
        source="product",
    )
    quantity    = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))
    cost_price  = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=Decimal("0"))
    sell_price  = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=Decimal("0"))

    def validate(self, attrs):
        if attrs["sell_price"] < attrs["cost_price"]:
            raise serializers.ValidationError(
                {"sell_price": "Sotish narxi tan narxidan kam bo'lmasligi kerak."}
            )
        return attrs


# ─── PurchasePayment ──────────────────────────────────────────────────────────

class PurchasePaymentSerializer(serializers.ModelSerializer):
    paid_by_name = serializers.CharField(source="paid_by.full_name", read_only=True, default=None)

    class Meta:
        model  = PurchasePayment
        fields = ["id", "amount", "note", "paid_by", "paid_by_name", "created_at"]
        read_only_fields = ["id", "paid_by", "created_at"]


class PaySerializer(serializers.Serializer):
    """Qarz to'lash uchun."""
    amount = serializers.DecimalField(max_digits=16, decimal_places=2, min_value=Decimal("0.01"))
    note   = serializers.CharField(max_length=300, required=False, default="")


# ─── Purchase ─────────────────────────────────────────────────────────────────

class PurchaseListSerializer(serializers.ModelSerializer):
    company_name    = serializers.CharField(source="company.name",  read_only=True)
    branch_name     = serializers.CharField(source="branch.name",   read_only=True, default=None)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)
    status_display  = serializers.CharField(source="get_status_display", read_only=True)
    is_overdue      = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Purchase
        fields = [
            "id", "company_name", "branch_name",
            "invoice_no", "status", "status_display",
            "total_amount", "paid_amount", "debt_amount",
            "due_date", "is_overdue",
            "created_by_name", "created_at",
        ]


class PurchaseDetailSerializer(serializers.ModelSerializer):
    company_name    = serializers.CharField(source="company.name",  read_only=True)
    branch_name     = serializers.CharField(source="branch.name",   read_only=True, default=None)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)
    status_display  = serializers.CharField(source="get_status_display", read_only=True)
    is_overdue      = serializers.BooleanField(read_only=True)
    is_fully_paid   = serializers.BooleanField(read_only=True)
    items           = PurchaseItemSerializer(many=True, read_only=True)
    payments        = PurchasePaymentSerializer(many=True, read_only=True)

    class Meta:
        model  = Purchase
        fields = [
            "id", "company", "company_name", "branch", "branch_name",
            "invoice_no", "status", "status_display",
            "total_amount", "paid_amount", "debt_amount",
            "due_date", "is_overdue", "is_fully_paid",
            "received_at", "note",
            "items", "payments",
            "created_by", "created_by_name",
            "created_at", "updated_at",
        ]


class PurchaseCreateSerializer(serializers.Serializer):
    """Yangi xarid yaratish."""
    company_id  = serializers.IntegerField()
    branch_id   = serializers.IntegerField(required=False, allow_null=True, default=None)
    invoice_no  = serializers.CharField(max_length=100, required=False, default="")
    due_date    = serializers.DateField(required=False, allow_null=True, default=None)
    note        = serializers.CharField(max_length=1000, required=False, default="")
    items       = PurchaseItemCreateSerializer(many=True, min_length=1)

    def validate_company_id(self, value):
        from companies.models import Company
        if not Company.objects.filter(pk=value, deleted_at__isnull=True).exists():
            raise serializers.ValidationError("Kompaniya topilmadi.")
        return value

    def validate_branch_id(self, value):
        if value:
            from companies.models import Branch
            if not Branch.objects.filter(pk=value, deleted_at__isnull=True).exists():
                raise serializers.ValidationError("Filial topilmadi.")
        return value
