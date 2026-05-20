"""
History views testlari.
pytest -v history/tests/test_views.py
"""
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from history.models import AuditAction, AuditLog
from history.utils import audit_log
from users.models import UserRole
from users.tests.factories import AdminFactory, UserFactory

BASE = "/api/v1/history/"


def client(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


def make_logs(n=5):
    user = UserFactory()
    for i in range(n):
        audit_log(
            action      = AuditAction.CREATE,
            user        = user,
            model_name  = "Product",
            object_id   = i + 1,
            object_repr = f"Product {i + 1}",
        )
    return user


@pytest.mark.django_db
class TestAuditLogList:

    def test_admin_can_list(self):
        admin = AdminFactory()
        make_logs(3)
        res = client(admin).get(BASE)
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["count"] >= 3

    def test_accountant_can_list(self):
        accountant = UserFactory(role=UserRole.ACCOUNTANT)
        make_logs(2)
        res = client(accountant).get(BASE)
        assert res.status_code == status.HTTP_200_OK

    def test_cashier_forbidden(self):
        cashier = UserFactory(role=UserRole.CASHIER)
        res     = client(cashier).get(BASE)
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_forbidden(self):
        res = APIClient().get(BASE)
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cannot_create(self):
        admin = AdminFactory()
        res   = client(admin).post(BASE, {}, format="json")
        assert res.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_cannot_delete(self):
        admin = AdminFactory()
        user  = make_logs(1)
        log   = AuditLog.objects.filter(user=user).first()
        res   = client(admin).delete(f"{BASE}{log.pk}/")
        assert res.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
class TestAuditLogFilters:

    def test_filter_by_action(self):
        admin = AdminFactory()
        user  = UserFactory()
        audit_log(action=AuditAction.LOGIN,  user=user, model_name="User", object_repr="Ali")
        audit_log(action=AuditAction.CREATE, user=user, model_name="Product", object_repr="Choy")

        res = client(admin).get(f"{BASE}?action=login")
        assert res.status_code == status.HTTP_200_OK
        for item in res.json()["results"]:
            assert item["action"] == AuditAction.LOGIN

    def test_filter_by_model(self):
        admin = AdminFactory()
        user  = UserFactory()
        audit_log(action=AuditAction.CREATE, model_name="Product", object_repr="Mahsulot")
        audit_log(action=AuditAction.CREATE, model_name="User",    object_repr="Foydalanuvchi")

        res = client(admin).get(f"{BASE}?model=Product")
        assert res.status_code == status.HTTP_200_OK
        for item in res.json()["results"]:
            assert item["model_name"] == "Product"

    def test_filter_by_user(self):
        admin  = AdminFactory()
        user1  = UserFactory()
        user2  = UserFactory()
        audit_log(action=AuditAction.LOGIN, user=user1, model_name="User", object_repr="1")
        audit_log(action=AuditAction.LOGIN, user=user2, model_name="User", object_repr="2")

        res = client(admin).get(f"{BASE}?user={user1.pk}")
        assert res.status_code == status.HTTP_200_OK
        for item in res.json()["results"]:
            assert item["user"] == user1.pk

    def test_filter_by_date(self):
        from datetime import date
        admin = AdminFactory()
        audit_log(
            action=AuditAction.CREATE,
            model_name="Test",
            object_repr="Today item",
        )
        today = date.today().isoformat()
        res   = client(admin).get(f"{BASE}?date_from={today}&date_to={today}")
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["count"] >= 1


@pytest.mark.django_db
class TestAuditLogDetail:

    def test_retrieve_log(self):
        admin = AdminFactory()
        log   = audit_log(
            action      = AuditAction.CREATE,
            model_name  = "Product",
            object_repr = "Test Product",
            extra       = {"sell_price": "5000"},
        )
        res = client(admin).get(f"{BASE}{log.pk}/")
        assert res.status_code == status.HTTP_200_OK
        data = res.json()
        assert data["model_name"]  == "Product"
        assert data["extra"]["sell_price"] == "5000"
