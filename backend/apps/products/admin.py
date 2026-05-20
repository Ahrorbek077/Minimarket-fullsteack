from django.contrib import admin
from .models import Category, Product, Unit


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display  = ["name", "short_name", "created_at"]
    search_fields = ["name", "short_name"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ["name", "parent", "icon", "order", "created_at"]
    list_filter   = ["parent"]
    search_fields = ["name"]
    ordering      = ["order", "name"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = [
        "name", "barcode", "category", "unit",
        "cost_price", "sell_price", "is_active",
    ]
    list_filter   = ["category", "is_active", "unit"]
    search_fields = ["name", "barcode"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (None, {"fields": ("name", "barcode", "description", "image")}),
        ("Kategoriya va o'lchov", {"fields": ("category", "unit")}),
        ("Narxlar", {"fields": ("cost_price", "sell_price", "min_stock")}),
        ("Holat", {"fields": ("is_active", "created_at", "updated_at")}),
    )
