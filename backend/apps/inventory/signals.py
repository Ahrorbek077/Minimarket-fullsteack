"""
Inventory signallari.

Product yaratilganda avtomatik Stock yaratiladi.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender="products.Product")
def create_stock_on_product_save(sender, instance, created, **kwargs):
    """Yangi mahsulot → Stock(quantity=0) avtomatik yaratiladi."""
    if created:
        from .models import Stock
        Stock.objects.get_or_create(
            product=instance,
            defaults={"quantity": 0},
        )
