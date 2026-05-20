"""
Companies model testlari.
pytest -v companies/tests/test_models.py
"""
import pytest
from companies.models import Branch, Company
from .factories import BranchFactory, CompanyFactory


@pytest.mark.django_db
class TestCompanyModel:

    def test_create_company(self):
        company = CompanyFactory(name="Coca-Cola UZ")
        assert company.pk is not None
        assert str(company) == "Coca-Cola UZ"

    def test_branch_count_property(self):
        company = CompanyFactory()
        BranchFactory.create_batch(3, company=company)
        assert company.branch_count == 3

    def test_branch_count_excludes_deleted(self):
        company = CompanyFactory()
        b1 = BranchFactory(company=company)
        b2 = BranchFactory(company=company)
        b2.delete()
        assert company.branch_count == 1

    def test_soft_delete(self):
        company = CompanyFactory()
        company.delete()
        assert Company.objects.filter(pk=company.pk).count() == 0
        assert Company.all_objects.filter(pk=company.pk).count() == 1

    def test_soft_delete_cascades_to_branches(self):
        """Kompaniya o'chirilsa filiallar ham o'chadi."""
        from companies.services import CompanyService
        company = CompanyFactory()
        b1 = BranchFactory(company=company)
        b2 = BranchFactory(company=company)
        CompanyService.soft_delete(company)
        assert Branch.objects.filter(company=company).count() == 0


@pytest.mark.django_db
class TestBranchModel:

    def test_create_branch(self):
        branch = BranchFactory(name="Toshkent filiali")
        assert branch.pk is not None
        assert "Toshkent filiali" in str(branch)

    def test_str_includes_company_name(self):
        company = CompanyFactory(name="Pepsi")
        branch  = BranchFactory(company=company, name="Samarqand")
        assert str(branch) == "Pepsi — Samarqand"

    def test_soft_delete(self):
        branch = BranchFactory()
        branch.delete()
        assert Branch.objects.filter(pk=branch.pk).count() == 0

    def test_unique_name_per_company(self):
        """Bir kompaniyada bir xil nomli filial bo'lmaydi."""
        company = CompanyFactory()
        BranchFactory(company=company, name="Asosiy")
        with pytest.raises(Exception):
            BranchFactory(company=company, name="Asosiy")

    def test_same_name_different_company_allowed(self):
        """Boshqa kompaniyada bir xil nom bo'lishi mumkin."""
        c1 = CompanyFactory()
        c2 = CompanyFactory()
        BranchFactory(company=c1, name="Asosiy")
        b2 = BranchFactory(company=c2, name="Asosiy")
        assert b2.pk is not None
