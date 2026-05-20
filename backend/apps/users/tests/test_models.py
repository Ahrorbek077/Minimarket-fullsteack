"""
User model testlari.
pytest -v apps/users/tests/test_models.py
"""
import pytest
from django.utils import timezone

from users.models import User, UserRole, UserLanguage
from .factories import UserFactory, AdminFactory, SuperAdminFactory


@pytest.mark.django_db
class TestUserModel:
    """User model uchun testlar."""

    def test_create_user_success(self):
        """Oddiy user muvaffaqiyatli yaratiladi."""
        user = User.objects.create_user(
            email="test@example.com",
            password="StrongPass123!",
            full_name="Test User",
        )
        assert user.pk is not None
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.role == UserRole.CASHIER  # default
        assert user.language == UserLanguage.UZ  # default
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_password_is_hashed(self):
        """Parol hash bo'lishi kerak."""
        user = UserFactory()
        assert user.password != "Test1234!"
        assert user.check_password("Test1234!") is True

    def test_create_user_email_normalized(self):
        """Email kichik harfga o'giriladi."""
        user = User.objects.create_user(
            email="Test@EXAMPLE.COM",
            password="pass123!A",
            full_name="Test",
        )
        assert user.email == "Test@example.com"

    def test_create_user_without_email_raises(self):
        """Email bo'lmasa ValueError."""
        with pytest.raises(ValueError, match="Email majburiy"):
            User.objects.create_user(email="", password="pass")

    def test_create_superuser(self):
        """Superuser to'g'ri yaratiladi."""
        user = User.objects.create_superuser(
            email="super@test.com",
            password="Super123!",
            full_name="Super Admin",
        )
        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.role == UserRole.SUPER_ADMIN

    def test_str_method(self):
        """__str__ to'g'ri formatda."""
        user = UserFactory(email="john@test.com", full_name="John Doe")
        assert str(user) == "John Doe <john@test.com>"

    def test_is_super_admin_property(self):
        """is_super_admin property."""
        super_admin = SuperAdminFactory()
        cashier     = UserFactory()
        assert super_admin.is_super_admin is True
        assert cashier.is_super_admin is False

    def test_is_admin_property(self):
        """is_admin — admin va super admin uchun True."""
        super_admin = SuperAdminFactory()
        admin       = AdminFactory()
        cashier     = UserFactory()
        assert super_admin.is_admin is True
        assert admin.is_admin is True
        assert cashier.is_admin is False

    def test_soft_delete(self):
        """Soft delete — DB dan o'chmaydi."""
        user = UserFactory()
        user_id = user.pk
        user.soft_delete()

        # is_active False bo'ldi
        assert user.is_active is False
        assert user.deleted_at is not None

        # DB da hali bor — all_objects orqali
        assert User.all_objects.filter(pk=user_id).count() == 1
        # Active userlar orasida yo'q
        assert User.objects.active().filter(pk=user_id).count() == 0

    def test_restore_deleted_user(self):
        """O'chirilgan userni qaytarish."""
        user = UserFactory()
        user.soft_delete()
        assert user.is_active is False

        user.restore()
        assert user.is_active is True
        assert user.deleted_at is None

    def test_is_deleted_property(self):
        """is_deleted property."""
        user = UserFactory()
        assert user.is_deleted is False
        user.soft_delete()
        assert user.is_deleted is True

    def test_get_full_name(self):
        user = UserFactory(full_name="Ali Valiyev")
        assert user.get_full_name() == "Ali Valiyev"

    def test_get_short_name(self):
        user = UserFactory(full_name="Ali Valiyev")
        assert user.get_short_name() == "Ali"

    def test_get_short_name_empty(self):
        """Ism bo'lmasa email qaytaradi."""
        user = UserFactory(full_name="", email="ali@test.com")
        assert user.get_short_name() == "ali@test.com"


@pytest.mark.django_db
class TestUserManager:
    """UserManager testlari."""

    def test_active_manager(self):
        """active() faqat faol userlarni qaytaradi."""
        active_user   = UserFactory()
        deleted_user  = UserFactory()
        deleted_user.soft_delete()

        active_users = User.objects.active()
        assert active_user in active_users
        assert deleted_user not in active_users

    def test_objects_excludes_deleted(self):
        """active() manager o'chirilganlarni ko'rsatmaydi."""
        user = UserFactory()
        user.soft_delete()
        assert User.objects.active().filter(pk=user.pk).count() == 0

    def test_all_objects_includes_deleted(self):
        """all_objects barchangi ko'rsatadi."""
        user = UserFactory()
        user.soft_delete()
        assert User.all_objects.filter(pk=user.pk).count() == 1
