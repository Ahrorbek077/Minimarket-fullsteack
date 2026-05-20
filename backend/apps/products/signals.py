"""
Products signallari.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Product


@receiver(post_save, sender=Product)
def product_post_save(sender, instance, created, **kwargs):
    """
    Yangi mahsulot yaratilganda Stock avtomatik yaratiladi.
    (inventory app qo'shilgach)
    """
    if created:
        # TODO: inventory app qo'shilgach:
        # from inventory.models import Stock
        # Stock.objects.get_or_create(product=instance, defaults={"quantity": 0})
        pass
