"""
Core models — barcha applar uchun asos.
BaseModel: created_at, updated_at, soft delete.
"""
from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    """Faqat o'chirilmagan objectlarni qaytaradi."""

    def delete(self):
        """Soft delete — deleted_at ni set qiladi."""
        return super().update(deleted_at=timezone.now())

    def hard_delete(self):
        """Haqiqiy o'chirish — faqat kerak bo'lganda ishlatiladi."""
        return super().delete()

    def alive(self):
        """O'chirilmagan objectlar."""
        return self.filter(deleted_at__isnull=True)

    def dead(self):
        """O'chirilgan objectlar."""
        return self.filter(deleted_at__isnull=False)


class SoftDeleteManager(models.Manager):
    """Default manager — faqat alive objectlarni ko'rsatadi."""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).alive()


class BaseModel(models.Model):
    """
    Barcha modellar uchun asos klass.

    Fields:
        created_at  — yaratilgan vaqt (auto)
        updated_at  — yangilangan vaqt (auto)
        deleted_at  — o'chirilgan vaqt (None = alive)
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    # Default manager — faqat alive objectlar
    objects = SoftDeleteManager()

    # Barcha objectlar (o'chirilganlar ham)
    all_objects = models.Manager.from_queryset(SoftDeleteQuerySet)()

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def delete(self, using=None, keep_parents=False):
        """Soft delete — DB dan o'chirmaydi."""
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def hard_delete(self):
        """Haqiqiy o'chirish — ehtiyotkorlik bilan ishlatilsin."""
        super().delete()

    def restore(self):
        """O'chirilgan objectni qaytarish."""
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
