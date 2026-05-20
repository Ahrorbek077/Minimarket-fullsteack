"""
User views testlari — CRUD, profile, parol.
pytest -v apps/users/tests/test_views.py
"""
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from users.models import User, UserRole
from .factories import (
    UserFactory, AdminFactory, SuperAdminFactory, StorekeeperFactory
)

BASE_URL = "/api/v1/auth/users/"
ME_URL   = "/api/v1/auth/me/"


def get_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
class TestUserList:
    """User ro'yxati — faqat admin+."""

    def test_admin_can_list_users(self):
        admin = AdminFactory()
        UserFactory.create_batch(3)
        res = get_client(admin).get(BASE_URL)
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["count"] >= 3

    def test_cashier_cannot_list_users(self):
        cashier = UserFactory()
        res = get_client(cashier).get(BASE_URL)
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_super_admin_sees_all_roles(self):
        super_admin = SuperAdminFactory()
        AdminFactory()
        UserFactory()
        res = get_client(super_admin).get(BASE_URL)
        assert res.status_code == status.HTTP_200_OK

    def test_admin_cannot_see_super_admins(self):
        """Admin super adminlarni ko'rmaydi."""
        admin = AdminFactory()
        super_admin = SuperAdminFactory()
        res = get_client(admin).get(BASE_URL)
        assert res.status_code == status.HTTP_200_OK
        emails = [u["email"] for u in res.json()["results"]]
        assert super_admin.email not in emails


@pytest.mark.django_db
class TestUserCreate:
    """User yaratish."""

    def test_admin_creates_user_success(self):
        admin = AdminFactory()
        payload = {
            "email": "newuser@test.com",
            "full_name": "New User",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
            "role": UserRole.CASHIER,
        }
        res = get_client(admin).post(BASE_URL, payload, format="json")
        assert res.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email="newuser@test.com").exists()

    def test_password_not_returned_in_response(self):
        admin = AdminFactory()
        payload = {
            "email": "secure@test.com",
            "full_name": "Secure User",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
            "role": UserRole.CASHIER,
        }
        res = get_client(admin).post(BASE_URL, payload, format="json")
        assert "password" not in res.json()

    def test_duplicate_email_returns_400(self):
        admin  = AdminFactory()
        existing = UserFactory(email="exists@test.com")
        payload  = {
            "email": "exists@test.com",
            "full_name": "Dup User",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
            "role": UserRole.CASHIER,
        }
        res = get_client(admin).post(BASE_URL, payload, format="json")
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_mismatch_returns_400(self):
        admin   = AdminFactory()
        payload = {
            "email": "nomatch@test.com",
            "full_name": "No Match",
            "password": "StrongPass123!",
            "password_confirm": "DifferentPass456!",
            "role": UserRole.CASHIER,
        }
        res = get_client(admin).post(BASE_URL, payload, format="json")
        assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserSoftDelete:
    """User soft delete."""

    def test_delete_user_soft(self):
        """O'chirish — DB dan ketmaydi, inactive bo'ladi."""
        from users.models import User
        super_admin = SuperAdminFactory()
        user        = UserFactory()
        user_pk     = user.pk

        # User DB da borligini tekshiramiz
        assert User.all_objects.filter(pk=user_pk).exists()

        res = get_client(super_admin).delete(f"{BASE_URL}{user_pk}/")
        assert res.status_code == status.HTTP_200_OK

        # Soft delete tekshirish
        assert User.all_objects.filter(pk=user_pk, is_active=False).exists()
        assert User.all_objects.filter(pk=user_pk, deleted_at__isnull=False).exists()

    def test_deleted_user_not_in_list(self):
        """O'chirilgan user ro'yxatda ko'rinmaydi."""
        admin   = AdminFactory()
        user    = UserFactory()
        user_pk = user.pk
        get_client(admin).delete(f"{BASE_URL}{user_pk}/")

        res = get_client(admin).get(BASE_URL)
        ids = [u["id"] for u in res.json()["results"]]
        assert user_pk not in ids


@pytest.mark.django_db
class TestProfile:
    """Profil testlari."""

    def test_get_own_profile(self):
        user = UserFactory(full_name="Ali Karimov")
        res  = get_client(user).get(f"{ME_URL}profile/")
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["data"]["full_name"] == "Ali Karimov"

    def test_update_own_profile(self):
        user = UserFactory()
        res  = get_client(user).patch(
            f"{ME_URL}update_profile/",
            {"full_name": "Yangi Ism"},
            format="json",
        )
        assert res.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.full_name == "Yangi Ism"

    def test_update_language(self):
        user = UserFactory()
        res  = get_client(user).patch(
            f"{ME_URL}update_profile/",
            {"language": "ru"},
            format="json",
        )
        assert res.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.language == "ru"


@pytest.mark.django_db
class TestChangePassword:
    """Parol almashtirish testlari."""

    def test_change_password_success(self):
        user = UserFactory()
        res  = get_client(user).post(
            f"{ME_URL}change-password/",
            {
                "old_password":          "Test1234!",
                "new_password":          "NewPass456!",
                "new_password_confirm":  "NewPass456!",
            },
            format="json",
        )
        assert res.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password("NewPass456!") is True

    def test_wrong_old_password(self):
        user = UserFactory()
        res  = get_client(user).post(
            f"{ME_URL}change-password/",
            {
                "old_password":         "WrongOld!",
                "new_password":         "NewPass456!",
                "new_password_confirm": "NewPass456!",
            },
            format="json",
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_new_passwords_mismatch(self):
        user = UserFactory()
        res  = get_client(user).post(
            f"{ME_URL}change-password/",
            {
                "old_password":         "Test1234!",
                "new_password":         "NewPass456!",
                "new_password_confirm": "Different789!",
            },
            format="json",
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_weak_new_password(self):
        """Zaif yangi parol — validator xato beradi."""
        user = UserFactory()
        res  = get_client(user).post(
            f"{ME_URL}change-password/",
            {
                "old_password":         "Test1234!",
                "new_password":         "123",
                "new_password_confirm": "123",
            },
            format="json",
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPermissions:
    """Role-based permission testlari."""

    def test_cashier_forbidden_from_user_create(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        payload = {
            "email": "new@test.com", "full_name": "New",
            "password": "Pass123!", "password_confirm": "Pass123!",
            "role": UserRole.CASHIER,
        }
        res = get_client(cashier).post(BASE_URL, payload, format="json")
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_storekeeper_forbidden_from_user_list(self):
        storekeeper = StorekeeperFactory()
        res = get_client(storekeeper).get(BASE_URL)
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_forbidden(self):
        client = APIClient()
        res    = client.get(BASE_URL)
        assert res.status_code == status.HTTP_401_UNAUTHORIZED
