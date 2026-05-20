"""
Custom permission classlar — role-based access control.
"""
from rest_framework.permissions import BasePermission

from users.models import UserRole


class IsSuperAdmin(BasePermission):
    """Faqat super admin."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == UserRole.SUPER_ADMIN
        )


class IsAdminOrAbove(BasePermission):
    """Admin va super admin."""
    ALLOWED_ROLES = {UserRole.SUPER_ADMIN, UserRole.ADMIN}

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in self.ALLOWED_ROLES
        )


class IsCashier(BasePermission):
    """Kassir — faqat kassa operatsiyalari."""
    ALLOWED_ROLES = {UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.CASHIER}

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in self.ALLOWED_ROLES
        )


class IsStorekeeper(BasePermission):
    """Omborchi — ombor operatsiyalari."""
    ALLOWED_ROLES = {UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.STOREKEEPER}

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in self.ALLOWED_ROLES
        )


class IsAccountant(BasePermission):
    """Buxgalter — hisobotlar."""
    ALLOWED_ROLES = {
        UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.ACCOUNTANT
    }

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in self.ALLOWED_ROLES
        )


class IsOwnerOrAdmin(BasePermission):
    """Object egasi yoki admin."""
    def has_object_permission(self, request, view, obj):
        if request.user.role in {UserRole.SUPER_ADMIN, UserRole.ADMIN}:
            return True
        return obj == request.user or getattr(obj, "user", None) == request.user


# ─── Throttle classes ─────────────────────────────────────────────────────────

from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """
    Login endpoint uchun: IP bo'yicha daqiqada 10 ta urinish.
    Brute force hujumidan himoya.
    """
    scope = "login"
