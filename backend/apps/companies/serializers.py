"""
Companies serializers.
"""
from rest_framework import serializers

from .models import Branch, Company


# ─── Branch ───────────────────────────────────────────────────────────────────

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Branch
        fields = ["id", "name", "phone", "address", "note", "created_at"]
        read_only_fields = ["id", "created_at"]


class BranchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Branch
        fields = ["name", "phone", "address", "note"]

    def validate_name(self, value):
        """Bir kompaniyada bir xil nomli filial bo'lmasligi kerak."""
        company = self.context.get("company")
        if company:
            qs = Branch.objects.filter(
                company=company,
                name=value,
                deleted_at__isnull=True,
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "Bu kompaniyada bunday nomli filial allaqachon mavjud."
                )
        return value


# ─── Company ──────────────────────────────────────────────────────────────────

class CompanyListSerializer(serializers.ModelSerializer):
    branch_count = serializers.SerializerMethodField()

    class Meta:
        model  = Company
        fields = [
            "id", "name", "phone", "address",
            "inn", "branch_count", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_branch_count(self, obj) -> int:
        # annotatsiya yoki property orqali
        if hasattr(obj, "branch_count_ann"):
            return obj.branch_count_ann
        return obj.branch_count


class CompanyDetailSerializer(serializers.ModelSerializer):
    branches        = BranchSerializer(many=True, read_only=True)
    branch_count    = serializers.SerializerMethodField()
    total_debt      = serializers.SerializerMethodField()

    class Meta:
        model  = Company
        fields = [
            "id", "name", "phone", "address", "inn",
            "note", "branch_count", "total_debt",
            "branches", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_branch_count(self, obj) -> int:
        if hasattr(obj, "branch_count_ann"):
            return obj.branch_count_ann or 0
        return obj.branch_count

    def get_total_debt(self, obj):
        # Annotatsiya bo'lsa ishlatamiz (N+1 yo'q), bo'lmasa property
        if hasattr(obj, "total_debt_ann"):
            from decimal import Decimal
            return str(obj.total_debt_ann or Decimal("0"))
        return str(obj.total_debt)


class CompanyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Company
        fields = ["name", "phone", "address", "inn", "note"]

    def validate_name(self, value):
        qs = Company.objects.filter(name__iexact=value, deleted_at__isnull=True)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Bu nomli kompaniya allaqachon mavjud.")
        return value
