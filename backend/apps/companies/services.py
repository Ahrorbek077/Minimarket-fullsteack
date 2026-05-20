"""
Companies services — biznes logika.
"""
from django.db import transaction
from django.utils import timezone

from core.exceptions import BusinessLogicError
from .models import Branch, Company


class CompanyService:

    @staticmethod
    def get_queryset():
        from django.db.models import Count, Q, Sum
        return (
            Company.objects
            .filter(deleted_at__isnull=True)
            .annotate(
                branch_count_ann=Count(
                    "branches",
                    filter=Q(branches__deleted_at__isnull=True),
                ),
                # total_debt — DB da bir query da hisoblanadi (N+1 yo'q)
                total_debt_ann=Sum(
                    "purchases__debt_amount",
                    filter=Q(
                        purchases__deleted_at__isnull=True,
                        purchases__debt_amount__gt=0,
                    ),
                ),
            )
            .order_by("name")
        )

    @staticmethod
    @transaction.atomic
    def create(validated_data: dict) -> Company:
        return Company.objects.create(**validated_data)

    @staticmethod
    @transaction.atomic
    def update(company: Company, validated_data: dict) -> Company:
        for field, value in validated_data.items():
            setattr(company, field, value)
        company.save()
        return company

    @staticmethod
    def soft_delete(company: Company) -> None:
        """Kompaniya va uning barcha filiallarini o'chirish."""
        company.branches.filter(deleted_at__isnull=True).update(
            deleted_at=timezone.now()
        )
        company.delete()


class BranchService:

    @staticmethod
    def get_for_company(company: Company):
        return Branch.objects.filter(
            company=company,
            deleted_at__isnull=True,
        ).order_by("name")

    @staticmethod
    def get_by_id(branch_id: int, company: Company = None) -> Branch:
        qs = Branch.objects.filter(pk=branch_id, deleted_at__isnull=True)
        if company:
            qs = qs.filter(company=company)
        branch = qs.select_related("company").first()
        if not branch:
            raise BusinessLogicError("Filial topilmadi.", "not_found")
        return branch

    @staticmethod
    @transaction.atomic
    def create(company: Company, validated_data: dict) -> Branch:
        return Branch.objects.create(company=company, **validated_data)

    @staticmethod
    @transaction.atomic
    def update(branch: Branch, validated_data: dict) -> Branch:
        for field, value in validated_data.items():
            setattr(branch, field, value)
        branch.save()
        return branch
