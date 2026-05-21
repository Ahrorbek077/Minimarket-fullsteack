"""
Sales serializers.
"""
from decimal import Decimal
from rest_framework import serializers
from .models import PaymentMethod, Sale, SaleItem, SalePayment, SaleStatus


# ─── Cart ─────────────────────────────────────────────────────────────────────

class CartItemSerializer(serializers.Serializer):
    product_id  = serializers.IntegerField()
    name        = serializers.CharField()
    barcode     = serializers.CharField()
    sell_price  = serializers.DecimalField(max_digits=14, decimal_places=2)
    quantity    = serializers.DecimalField(max_digits=12, decimal_places=2)
    unit_short  = serializers.CharField()
    subtotal    = serializers.DecimalField(max_digits=16, decimal_places=2)


class CartSerializer(serializers.Serializer):
    items        = CartItemSerializer(many=True)
    item_count   = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=16, decimal_places=2)


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity   = serializers.DecimalField(
        max_digits=12, decimal_places=2,
        min_value=Decimal("0.01"),
        default=Decimal("1"),
    )


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("0")
    )


class ScanBarcodeSerializer(serializers.Serializer):
    barcode  = serializers.CharField()
    quantity = serializers.DecimalField(
        max_digits=12, decimal_places=2,
        min_value=Decimal("0.01"),
        default=Decimal("1"),
    )


# ─── Payment ──────────────────────────────────────────────────────────────────

class SalePaymentSerializer(serializers.ModelSerializer):
    method_display = serializers.CharField(source="get_method_display", read_only=True)

    class Meta:
        model  = SalePayment
        fields = ["id", "method", "method_display", "amount"]
        read_only_fields = fields


class PaymentInputSerializer(serializers.Serializer):
    method = serializers.ChoiceField(choices=PaymentMethod.choices)
    amount = serializers.DecimalField(
        max_digits=16, decimal_places=2, min_value=Decimal("0.01")
    )


# ─── Checkout ─────────────────────────────────────────────────────────────────

class CheckoutSerializer(serializers.Serializer):
    payments     = PaymentInputSerializer(many=True, min_length=1)
    discount_pct = serializers.DecimalField(
        max_digits=5, decimal_places=2,
        min_value=Decimal("0"), max_value=Decimal("100"),
        default=Decimal("0"),
    )
    note = serializers.CharField(max_length=500, required=False, default="", allow_blank=True)


# ─── SaleItem ─────────────────────────────────────────────────────────────────

class SaleItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name",             read_only=True)
    unit_short   = serializers.CharField(source="product.unit.short_name",  read_only=True, default=None)

    class Meta:
        model  = SaleItem
        fields = [
            "id", "product", "product_name", "unit_short",
            "quantity", "sell_price", "cost_price_snapshot", "total",
        ]
        read_only_fields = fields


# ─── Sale ─────────────────────────────────────────────────────────────────────

class SaleListSerializer(serializers.ModelSerializer):
    cashier_name   = serializers.CharField(source="cashier.full_name", read_only=True, default=None)
    status_display = serializers.CharField(source="get_status_display",   read_only=True)
    payment_methods = serializers.SerializerMethodField()

    class Meta:
        model  = Sale
        fields = [
            "id", "invoice_no", "status", "status_display",
            "total_amount", "discount_pct", "discount_amount",
            "net_amount", "paid_amount", "debt_amount",
            "payment_methods", "cashier_name", "created_at",
        ]

    def get_payment_methods(self, obj) -> list:
        return list(
            obj.payments.values_list("method", flat=True).distinct()
        )


class SaleDetailSerializer(serializers.ModelSerializer):
    cashier_name    = serializers.CharField(source="cashier.full_name", read_only=True, default=None)
    status_display  = serializers.CharField(source="get_status_display",   read_only=True)
    items           = SaleItemSerializer(many=True, read_only=True)
    payments        = SalePaymentSerializer(many=True, read_only=True)
    is_debt         = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Sale
        fields = [
            "id", "invoice_no", "status", "status_display",
            "total_amount", "discount_pct", "discount_amount",
            "net_amount", "paid_amount", "debt_amount", "is_debt",
            "cashier", "cashier_name",
            "items", "payments",
            "note", "created_at", "updated_at",
        ]


# ─── Return ───────────────────────────────────────────────────────────────────

class ReturnItemSerializer(serializers.Serializer):
    sale_item_id = serializers.IntegerField()
    quantity     = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("0.01")
    )


class ReturnSaleSerializer(serializers.Serializer):
    items  = ReturnItemSerializer(many=True, required=False)  # None = to'liq
    reason = serializers.CharField(max_length=300, required=False, default="")
