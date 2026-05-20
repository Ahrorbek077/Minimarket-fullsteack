"""
AuditLog yozish uchun utility funksiyalar.

Ishlatish:
    from history.utils import audit_log

    audit_log(
        user       = request.user,
        action     = AuditAction.CREATE,
        instance   = product,
        request    = request,   # IP uchun, ixtiyoriy
        extra      = {"invoice_no": sale.invoice_no},
    )
"""
from typing import Any

from .models import AuditAction, AuditLog


def _get_repr(instance) -> str:
    """Model instancening string ko'rinishi."""
    try:
        return str(instance)[:255]
    except Exception:
        return f"#{getattr(instance, 'pk', '?')}"


def _get_ip(request) -> str | None:
    if request is None:
        return None
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _diff(old: dict, new: dict) -> dict:
    """
    Ikki dict o'rtasidagi farqni topish.
    Qaytaradi: {field: [old_val, new_val]}
    """
    changes = {}
    all_keys = set(old) | set(new)
    for key in all_keys:
        old_val = old.get(key)
        new_val = new.get(key)
        if str(old_val) != str(new_val):
            changes[key] = [str(old_val), str(new_val)]
    return changes


def audit_log(
    action: str,
    user=None,
    instance=None,
    model_name: str = "",
    object_id: int | None = None,
    object_repr: str = "",
    changes: dict | None = None,
    request=None,
    extra: dict | None = None,
) -> AuditLog:
    """
    AuditLog yozuv yaratish.

    Parametrlar:
        action      — AuditAction qiymati
        user        — kim bajardi (None = tizim)
        instance    — model instance (model_name va object_id avtomatik olinadi)
        model_name  — instance bo'lmasa qo'lda
        object_id   — instance bo'lmasa qo'lda
        object_repr — instance bo'lmasa qo'lda
        changes     — {"field": [old, new]} — UPDATE uchun
        request     — IP manzil olish uchun
        extra       — qo'shimcha JSON ma'lumot
    """
    if instance is not None:
        model_name  = model_name  or instance.__class__.__name__
        object_id   = object_id   or getattr(instance, "pk", None)
        object_repr = object_repr or _get_repr(instance)

    return AuditLog.objects.create(
        user        = user,
        action      = action,
        model_name  = model_name,
        object_id   = object_id,
        object_repr = object_repr,
        changes     = changes or {},
        ip_address  = _get_ip(request),
        extra       = extra or {},
    )


def audit_update(
    user,
    instance,
    old_data: dict,
    new_data: dict,
    request=None,
    extra: dict | None = None,
) -> AuditLog | None:
    """
    UPDATE uchun — faqat farq bo'lsa yozadi.
    Farq yo'q bo'lsa None qaytaradi.
    """
    changes = _diff(old_data, new_data)
    if not changes:
        return None
    return audit_log(
        action   = AuditAction.UPDATE,
        user     = user,
        instance = instance,
        changes  = changes,
        request  = request,
        extra    = extra,
    )
