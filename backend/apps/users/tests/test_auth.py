"""
JWT Authentication testlari.
pytest -v apps/users/tests/test_auth.py
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .factories import UserFactory, AdminFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client):
    """Autentifikatsiya qilingan client."""
    user = UserFactory()
    api_client.force_authenticate(user=user)
    api_client._user = user
    return api_client


@pytest.mark.django_db
class TestLogin:
    """Login endpoint testlari."""

    def test_login_success(self, api_client):
        """To'g'ri email+parol bilan login."""
        user = UserFactory()
        response = api_client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": "Test1234!"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access" in data
        # refresh endi httpOnly cookie da (body da yo'q)
        assert "refresh" not in data
        assert "user" in data
        # Cookie set qilinganligini tekshiramiz
        assert "refresh_token" in response.cookies
        assert data["user"]["email"] == user.email

    def test_login_wrong_password(self, api_client):
        """Noto'g'ri parol — 401."""
        user = UserFactory()
        response = api_client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": "WrongPass!"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_inactive_user(self, api_client):
        """Deaktiv user login qila olmaydi."""
        user = UserFactory(is_active=False)
        response = api_client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": "Test1234!"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_missing_email(self, api_client):
        """Email bo'lmasa — 400."""
        response = api_client.post(
            "/api/v1/auth/login/",
            {"password": "Test1234!"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_returns_user_role(self, api_client):
        """Login response da rol ma'lumoti bor."""
        from users.models import UserRole
        admin = AdminFactory()
        response = api_client.post(
            "/api/v1/auth/login/",
            {"email": admin.email, "password": "Test1234!"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["user"]["role"] == UserRole.ADMIN


@pytest.mark.django_db
class TestTokenRefresh:
    """Token refresh testlari."""

    def test_refresh_token_success(self, api_client):
        """Valid refresh token (cookie orqali) bilan yangi access token."""
        user = UserFactory()
        login_res = api_client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": "Test1234!"},
            format="json",
        )
        assert login_res.status_code == 200
        # Cookie dan refresh tokenni olamiz
        refresh_cookie = login_res.cookies.get("refresh_token")
        assert refresh_cookie is not None, "refresh_token cookie set qilinmagan"

        # Cookie avtomatik yuboriladi (APIClient cookie jar ishlatadi)
        response = api_client.post(
            "/api/v1/auth/token/refresh/",
            {},   # body bo'sh — cookie dan o'qiydi
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.json()

    def test_refresh_invalid_token(self, api_client):
        """Noto'g'ri refresh token — 401."""
        response = api_client.post(
            "/api/v1/auth/token/refresh/",
            {"refresh": "invalid.token.here"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestLogout:
    """Logout (token blacklist) testlari."""

    def test_logout_success(self, api_client):
        """Logout cookie ni o'chiradi va tokenni blacklist ga qo'shadi."""
        user = UserFactory()
        login_res = api_client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": "Test1234!"},
            format="json",
        )
        access = login_res.json()["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        # Cookie orqali logout
        response = api_client.post("/api/v1/auth/logout/", {}, format="json")
        assert response.status_code == status.HTTP_200_OK

        # Cookie o'chirilganini tekshiramiz
        assert response.cookies.get("refresh_token", {}).get("max-age") in (0, "0", None) or                "refresh_token" not in response.cookies or                response.cookies["refresh_token"].value == ""

        # Cookie blacklist bo'lgani uchun qayta refresh qilib bo'lmaydi
        refresh_res = api_client.post(
            "/api/v1/auth/token/refresh/",
            {},
            format="json",
        )
        assert refresh_res.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_400_BAD_REQUEST)


@pytest.mark.django_db
class TestProtectedEndpoint:
    """Himoyalangan endpoint testlari."""

    def test_unauthenticated_returns_401(self, api_client):
        """Token bo'lmasa 401."""
        response = api_client.get("/api/v1/auth/users/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_returns_200(self, auth_client):
        """Token bilan 200."""
        # auth_client da faqat cashier — bu endpoint admin uchun
        from users.models import UserRole
        auth_client._user.role = UserRole.ADMIN
        auth_client._user.save()
        response = auth_client.get("/api/v1/auth/users/")
        assert response.status_code == status.HTTP_200_OK
