from django.contrib import admin
from .models import Stock, StockMovement


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display  = ["product", "quantity", "is_low", "updated_at"]
    search_fields = ["product__name", "product__barcode"]
    readonly_fields = ["updated_at"]

    def is_low(self, obj):
        return obj.is_low
    is_low.boolean = True
    is_low.short_description = "Kam?"


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display  = [
        "product", "movement_type", "quantity",
        "qty_before", "qty_after", "source_type", "created_by", "created_at",
    ]
    list_filter   = ["movement_type", "source_type"]
    search_fields = ["product__name", "reason"]
    readonly_fields = [
        "product", "movement_type", "quantity",
        "qty_before", "qty_after",
        "source_type", "source_id",
        "reason", "created_by", "created_at",
    ]

    def has_add_permission(self, request):
        return False  # Faqat o'qish — qo'lda qo'shib bo'lmaydi

    def has_delete_permission(self, request, obj=None):
        return False  # Tarixni o'chirish mumkin emas
