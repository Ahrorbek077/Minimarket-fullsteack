"""
Django admin — User modeli.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display    = ["email", "full_name", "role", "is_active", "date_joined"]
    list_filter     = ["role", "is_active", "language"]
    search_fields   = ["email", "full_name", "phone"]
    ordering        = ["-date_joined"]
    readonly_fields = ["date_joined", "created_at", "updated_at", "deleted_at"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Shaxsiy ma'lumot"), {"fields": ("full_name", "phone", "avatar")}),
        (_("Rol va til"), {"fields": ("role", "language")}),
        (_("Ruxsatlar"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Muhim sanalar"), {"fields": ("date_joined", "created_at", "updated_at", "deleted_at")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "full_name", "role", "password1", "password2"),
        }),
    )
