"""
UserService testlari.
pytest -v apps/users/tests/test_services.py
"""
import pytest

from users.models import User, UserRole
from users.services import UserService
from .factories import UserFactory, AdminFactory


@pytest.mark.django_db
class TestUserService:

    def test_create_user(self):
        user = UserService.create_user(
            email="service@test.com",
            password="ServicePass123!",
            full_name="Service User",
            role=UserRole.CASHIER,
        )
        assert user.pk is not None
        assert user.email == "service@test.com"
        assert user.role == UserRole.CASHIER

    def test_change_password(self):
        user = UserFactory()
        UserService.change_password(user, "NewStrongPass789!")
        user.refresh_from_db()
        assert user.check_password("NewStrongPass789!") is True
        assert not user.check_password("Test1234!")

    def test_soft_delete_user(self):
        user = UserFactory()
        UserService.soft_delete_user(user)
        user.refresh_from_db()
        assert user.is_active is False
        assert user.deleted_at is not None

    def test_get_active_users(self):
        active1   = UserFactory()
        active2   = UserFactory()
        deleted   = UserFactory()
        deleted.soft_delete()

        active_list = list(UserService.get_active_users())
        assert active1 in active_list
        assert active2 in active_list
        assert deleted not in active_list

    def test_update_profile(self):
        user = UserFactory(full_name="Old Name")
        updated = UserService.update_profile(user, full_name="New Name", language="ru")
        assert updated.full_name == "New Name"
        assert updated.language == "ru"

    def test_update_profile_ignores_unknown_fields(self):
        """Noto'g'ri field — xato bermasligi kerak."""
        user = UserFactory()
        # role ni o'zgartirish mumkin emas bu metod orqali
        UserService.update_profile(user, role=UserRole.SUPER_ADMIN)
        user.refresh_from_db()
        # role o'zgarmasligi kerak
        assert user.role == UserRole.CASHIER
