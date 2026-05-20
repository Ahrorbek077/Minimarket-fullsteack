from django.contrib import admin
from .models import Purchase, PurchaseItem, PurchasePayment


class PurchaseItemInline(admin.TabularInline):
    model  = PurchaseItem
    extra  = 0
    fields = ["product", "quantity", "cost_price", "sell_price", "total"]
    readonly_fields = ["total"]


class PurchasePaymentInline(admin.TabularInline):
    model  = PurchasePayment
    extra  = 0
    fields = ["amount", "note", "paid_by", "created_at"]
    readonly_fields = ["created_at"]


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display   = [
        "id", "company", "status", "total_amount",
        "paid_amount", "debt_amount", "due_date", "created_at",
    ]
    list_filter    = ["status", "company"]
    search_fields  = ["invoice_no", "company__name"]
    readonly_fields = ["total_amount", "paid_amount", "debt_amount", "received_at", "created_at"]
    inlines        = [PurchaseItemInline, PurchasePaymentInline]
