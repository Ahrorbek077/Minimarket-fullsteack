from django.contrib import admin
from .models import Branch, Company


class BranchInline(admin.TabularInline):
    model  = Branch
    extra  = 0
    fields = ["name", "phone", "address"]


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display  = ["name", "phone", "inn", "branch_count", "created_at"]
    search_fields = ["name", "inn", "phone"]
    inlines       = [BranchInline]
    readonly_fields = ["created_at", "updated_at"]

    def branch_count(self, obj):
        return obj.branches.filter(deleted_at__isnull=True).count()
    branch_count.short_description = "Filiallar"


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display  = ["name", "company", "phone", "created_at"]
    list_filter   = ["company"]
    search_fields = ["name", "company__name"]
