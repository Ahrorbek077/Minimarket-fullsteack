from django.contrib import admin
from .models import Sale, SaleItem, SalePayment


class SaleItemInline(admin.TabularInline):
    model       = SaleItem
    extra       = 0
    fields      = ["product", "quantity", "sell_price", "cost_price_snapshot", "total"]
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


class SalePaymentInline(admin.TabularInline):
    model       = SalePayment
    extra       = 0
    fields      = ["method", "amount"]
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display    = [
        "invoice_no", "status", "net_amount",
        "paid_amount", "debt_amount", "cashier", "created_at",
    ]
    list_filter     = ["status"]
    search_fields   = ["invoice_no", "cashier__full_name"]
    readonly_fields = [
        "invoice_no", "total_amount", "discount_amount",
        "net_amount", "paid_amount", "debt_amount", "created_at",
    ]
    inlines         = [SaleItemInline, SalePaymentInline]

    def has_add_permission(self, request):
        return False
