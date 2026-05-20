"""
User services — barcha biznes logika shu yerda.
View da logika bo'lmaydi.
"""
from django.contrib.auth.hashers import make_password
from django.utils import timezone

from .models import User, UserRole


class UserService:
    """
    User bilan bog'liq barcha operatsiyalar.
    """

    @staticmethod
    def create_user(
        email: str,
        password: str,
        full_name: str,
        role: str = UserRole.CASHIER,
        **kwargs,
    ) -> User:
        """Yangi user yaratish."""
        return User.objects.create_user(
            email=email,
            password=password,
            full_name=full_name,
            role=role,
            **kwargs,
        )

    @staticmethod
    def change_password(user: User, new_password: str) -> None:
        """Parolni almashtirish va barcha tokenlarni bekor qilish."""
        user.set_password(new_password)
        user.save(update_fields=["password", "updated_at"])

        # Barcha refresh tokenlarni blacklist qilish
        UserService._blacklist_all_tokens(user)

    @staticmethod
    def _blacklist_all_tokens(user: User) -> None:
        """Foydalanuvchining barcha refresh tokenlarini bekor qilish."""
        try:
            from rest_framework_simplejwt.token_blacklist.models import (
                OutstandingToken, BlacklistedToken
            )
            tokens = OutstandingToken.objects.filter(user=user)
            for token in tokens:
                BlacklistedToken.objects.get_or_create(token=token)
        except Exception:
            pass  # Token blacklist app o'rnatilmagan bo'lsa skip

    @staticmethod
    def soft_delete_user(user: User) -> None:
        """Userni o'chirish (deaktivatsiya)."""
        user.soft_delete()
        UserService._blacklist_all_tokens(user)

    @staticmethod
    def get_active_users():
        """Faol userlar ro'yxati."""
        return User.objects.filter(
            is_active=True,
            deleted_at__isnull=True,
        ).order_by("-date_joined")

    @staticmethod
    def update_profile(user: User, **kwargs) -> User:
        """Profilni yangilash."""
        allowed_fields = {"full_name", "phone", "avatar", "language"}
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(user, field, value)
        user.save(update_fields=list(kwargs.keys()) + ["updated_at"])
        return user
