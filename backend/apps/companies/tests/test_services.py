"""
Companies services testlari.
pytest -v companies/tests/test_services.py
"""
import pytest
from core.exceptions import BusinessLogicError
from companies.models import Branch
from companies.services import BranchService, CompanyService
from .factories import BranchFactory, CompanyFactory


@pytest.mark.django_db
class TestCompanyService:

    def test_create(self):
        company = CompanyService.create({"name": "Test Co", "phone": "+998901234567"})
        assert company.pk is not None

    def test_soft_delete_with_branches(self):
        company = CompanyFactory()
        BranchFactory.create_batch(2, company=company)
        CompanyService.soft_delete(company)
        assert Branch.objects.filter(company=company).count() == 0

    def test_get_queryset_excludes_deleted(self):
        c1 = CompanyFactory()
        c2 = CompanyFactory()
        c2.delete()
        qs = list(CompanyService.get_queryset())
        assert c1 in qs
        assert c2 not in qs


@pytest.mark.django_db
class TestBranchService:

    def test_create_branch(self):
        company = CompanyFactory()
        branch  = BranchService.create(company, {"name": "Filial 1"})
        assert branch.company == company

    def test_get_by_id_success(self):
        branch = BranchFactory()
        result = BranchService.get_by_id(branch.pk)
        assert result == branch

    def test_get_by_id_not_found(self):
        with pytest.raises(BusinessLogicError) as exc:
            BranchService.get_by_id(99999)
        assert exc.value.default_code == "not_found"

    def test_get_by_id_wrong_company(self):
        company1 = CompanyFactory()
        company2 = CompanyFactory()
        branch   = BranchFactory(company=company2)
        with pytest.raises(BusinessLogicError):
            BranchService.get_by_id(branch.pk, company=company1)

    def test_update_branch(self):
        branch  = BranchFactory(name="Eski nom")
        updated = BranchService.update(branch, {"name": "Yangi nom"})
        assert updated.name == "Yangi nom"
