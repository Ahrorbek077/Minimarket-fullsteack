"""
Inventory serializers.
"""
from rest_framework import serializers

from .models import MovementType, Stock, StockMovement


class StockSerializer(serializers.ModelSerializer):
    product_id      = serializers.IntegerField(source="product.id",               read_only=True)
    product_name    = serializers.CharField(source="product.name",                read_only=True)
    product_barcode = serializers.CharField(source="product.barcode",             read_only=True)
    unit_short      = serializers.CharField(source="product.unit.short_name",     read_only=True, default=None)
    category_name   = serializers.CharField(source="product.category.name",       read_only=True, default=None)
    cost_price      = serializers.DecimalField(
        source="product.cost_price", max_digits=14, decimal_places=2, read_only=True
    )
    sell_price      = serializers.DecimalField(
        source="product.sell_price", max_digits=14, decimal_places=2, read_only=True
    )
    min_stock       = serializers.DecimalField(
        source="product.min_stock", max_digits=12, decimal_places=2, read_only=True
    )
    cost_value      = serializers.SerializerMethodField()
    sell_value      = serializers.SerializerMethodField()
    is_low          = serializers.BooleanField(read_only=True)
    is_empty        = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Stock
        fields = [
            "id", "product", "product_id", "product_name", "product_barcode",
            "unit_short", "category_name",
            "quantity", "min_stock", "cost_price", "sell_price",
            "cost_value", "sell_value",
            "is_low", "is_empty", "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]

    def get_cost_value(self, obj):
        from decimal import Decimal
        return str(obj.quantity * obj.product.cost_price)

    def get_sell_value(self, obj):
        from decimal import Decimal
        return str(obj.quantity * obj.product.sell_price)


class StockAdjustSerializer(serializers.Serializer):
    """Manual tuzatish uchun."""
    new_quantity = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=0
    )
    reason = serializers.CharField(max_length=300, required=False, default="")


class StockMovementSerializer(serializers.ModelSerializer):
    product_name       = serializers.CharField(source="product.name",      read_only=True)
    unit_short         = serializers.CharField(
        source="product.unit.short_name", read_only=True, default=None
    )
    movement_type_display = serializers.CharField(
        source="get_movement_type_display", read_only=True
    )
    created_by_name    = serializers.CharField(
        source="created_by.full_name", read_only=True, default=None
    )

    class Meta:
        model  = StockMovement
        fields = [
            "id",
            "product", "product_name", "unit_short",
            "movement_type", "movement_type_display",
            "quantity", "qty_before", "qty_after",
            "source_type", "source_id",
            "reason",
            "created_by", "created_by_name",
            "created_at",
        ]
        read_only_fields = fields
