"""
Signal handlers — barcha applarning muhim voqealarini tinglash.

Har bir signal handler:
  1. Faqat o'z appining modelini tinglaydi
  2. audit_log() chaqiradi
  3. Xato bo'lsa — silent fail (sotuv buzilmasin)
"""
import logging

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AuditAction
from .utils import audit_log

logger = logging.getLogger(__name__)


def _safe_log(*args, **kwargs):
    """Xato bo'lsa log'ga yozib davom etadi."""
    try:
        audit_log(*args, **kwargs)
    except Exception as e:
        logger.error(f"AuditLog yozishda xato: {e}")


# ─── Auth ─────────────────────────────────────────────────────────────────────

@receiver(user_logged_in)
def on_login(sender, request, user, **kwargs):
    _safe_log(
        action      = AuditAction.LOGIN,
        user        = user,
        instance    = user,
        request     = request,
        extra       = {"email": user.email},
    )


@receiver(user_logged_out)
def on_logout(sender, request, user, **kwargs):
    if user:
        _safe_log(
            action   = AuditAction.LOGOUT,
            user     = user,
            instance = user,
            request  = request,
        )


# ─── User ─────────────────────────────────────────────────────────────────────

@receiver(post_save, sender="users.User")
def on_user_save(sender, instance, created, **kwargs):
    if created:
        _safe_log(
            action      = AuditAction.CREATE,
            instance    = instance,
            extra       = {"role": instance.role, "email": instance.email},
        )


# ─── Product ──────────────────────────────────────────────────────────────────

@receiver(post_save, sender="products.Product")
def on_product_save(sender, instance, created, **kwargs):
    if created:
        _safe_log(
            action   = AuditAction.CREATE,
            instance = instance,
            extra    = {
                "cost_price": str(instance.cost_price),
                "sell_price": str(instance.sell_price),
            },
        )


# ─── Purchase ─────────────────────────────────────────────────────────────────

@receiver(post_save, sender="purchases.Purchase")
def on_purchase_save(sender, instance, created, **kwargs):
    if created:
        _safe_log(
            action   = AuditAction.CREATE,
            instance = instance,
            extra    = {
                "company":      instance.company.name,
                "total_amount": str(instance.total_amount),
            },
        )
    else:
        # Status o'zgarishlarini kuzatish
        status_action_map = {
            "received":  AuditAction.PURCHASE_RECEIVED,
            "paid":      AuditAction.PURCHASE_PAID,
            "partial":   AuditAction.PURCHASE_PAID,
            "cancelled": AuditAction.PURCHASE_CANCELLED,
        }
        action = status_action_map.get(instance.status)
        if action:
            _safe_log(
                action   = action,
                instance = instance,
                extra    = {
                    "status":       instance.status,
                    "paid_amount":  str(instance.paid_amount),
                    "debt_amount":  str(instance.debt_amount),
                },
            )


# ─── Sale ─────────────────────────────────────────────────────────────────────

@receiver(post_save, sender="sales.Sale")
def on_sale_save(sender, instance, created, **kwargs):
    if created:
        _safe_log(
            action   = AuditAction.SALE_CHECKOUT,
            instance = instance,
            extra    = {
                "invoice_no": instance.invoice_no,
                "net_amount": str(instance.net_amount),
                "cashier":    instance.cashier.full_name if instance.cashier else None,
            },
        )
    else:
        if instance.status in ("returned", "partial"):
            _safe_log(
                action   = AuditAction.SALE_RETURN,
                instance = instance,
                extra    = {
                    "invoice_no": instance.invoice_no,
                    "status":     instance.status,
                },
            )
