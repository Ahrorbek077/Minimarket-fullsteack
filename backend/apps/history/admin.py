from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display  = [
        "action", "model_name", "object_repr",
        "user", "ip_address", "created_at",
    ]
    list_filter   = ["action", "model_name"]
    search_fields = ["object_repr", "user__full_name", "user__email"]
    readonly_fields = [
        "user", "action", "model_name", "object_id",
        "object_repr", "changes", "ip_address", "extra", "created_at",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
