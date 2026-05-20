from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Sale


@receiver(post_save, sender=Sale)
def sale_post_save(sender, instance, created, **kwargs):
    """Sale o'zgarishi → AuditLog (keyinchalik)."""
    pass
