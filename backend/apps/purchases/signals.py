"""
Purchases signallari — hozircha placeholder.
AuditLog app qo'shilgach to'ldiriladi.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Purchase


@receiver(post_save, sender=Purchase)
def purchase_post_save(sender, instance, created, **kwargs):
    """Purchase o'zgarishi → AuditLog (keyinchalik)."""
    pass
