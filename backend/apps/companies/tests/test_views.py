"""
Companies views testlari.
pytest -v companies/tests/test_views.py
"""
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from users.tests.factories import AdminFactory, UserFactory
from users.models import UserRole
from .factories import BranchFactory, CompanyFactory

BASE = "/api/v1/companies/"


def client(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@pytest.mark.django_db
class TestCompanyList:

    def test_admin_can_list(self):
        CompanyFactory.create_batch(3)
        res = client(AdminFactory()).get(BASE)
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["count"] >= 3

    def test_cashier_forbidden(self):
        res = client(UserFactory(role=UserRole.CASHIER)).get(BASE)
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_forbidden(self):
        assert APIClient().get(BASE).status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestCompanyCreate:

    def test_create_success(self):
        res = client(AdminFactory()).post(
            BASE, {"name": "Yangi Kompaniya", "phone": "+998901234567"}, format="json"
        )
        assert res.status_code == status.HTTP_201_CREATED

    def test_duplicate_name_returns_400(self):
        CompanyFactory(name="Duplikat")
        res = client(AdminFactory()).post(BASE, {"name": "Duplikat"}, format="json")
        assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestCompanyDetail:

    def test_detail_includes_branches(self):
        company = CompanyFactory()
        BranchFactory.create_batch(2, company=company)
        res = client(AdminFactory()).get(f"{BASE}{company.pk}/")
        assert res.status_code == status.HTTP_200_OK
        assert len(res.json()["branches"]) == 2

    def test_soft_delete(self):
        company = CompanyFactory()
        res = client(AdminFactory()).delete(f"{BASE}{company.pk}/")
        assert res.status_code == status.HTTP_200_OK
        from companies.models import Company
        company.refresh_from_db()
        assert company.deleted_at is not None


@pytest.mark.django_db
class TestBranchActions:

    def test_list_branches(self):
        company = CompanyFactory()
        BranchFactory.create_batch(3, company=company)
        res = client(AdminFactory()).get(f"{BASE}{company.pk}/branches/")
        assert res.status_code == status.HTTP_200_OK
        assert len(res.json()["data"]) == 3

    def test_add_branch(self):
        company = CompanyFactory()
        res = client(AdminFactory()).post(
            f"{BASE}{company.pk}/branches/add/",
            {"name": "Yangi filial", "phone": "+998901111111"},
            format="json",
        )
        assert res.status_code == status.HTTP_201_CREATED

    def test_duplicate_branch_name_returns_400(self):
        company = CompanyFactory()
        BranchFactory(company=company, name="Asosiy")
        res = client(AdminFactory()).post(
            f"{BASE}{company.pk}/branches/add/",
            {"name": "Asosiy"},
            format="json",
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_branch(self):
        company = CompanyFactory()
        branch  = BranchFactory(company=company)
        res = client(AdminFactory()).patch(
            f"{BASE}{company.pk}/branches/{branch.pk}/",
            {"name": "Yangilangan filial"},
            format="json",
        )
        assert res.status_code == status.HTTP_200_OK
        branch.refresh_from_db()
        assert branch.name == "Yangilangan filial"

    def test_delete_branch(self):
        company = CompanyFactory()
        branch  = BranchFactory(company=company)
        res = client(AdminFactory()).delete(
            f"{BASE}{company.pk}/branches/{branch.pk}/delete/"
        )
        assert res.status_code == status.HTTP_200_OK
        branch.refresh_from_db()
        assert branch.deleted_at is not None

    def test_branch_of_another_company_not_accessible(self):
        """Boshqa kompaniyaning filialiga kira olmaydi."""
        company1 = CompanyFactory()
        company2 = CompanyFactory()
        branch   = BranchFactory(company=company2)
        res = client(AdminFactory()).patch(
            f"{BASE}{company1.pk}/branches/{branch.pk}/",
            {"name": "Hack"},
            format="json",
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST
