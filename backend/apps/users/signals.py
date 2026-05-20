"""
User signallari — voqealar sodir bo'lganda avtomatik ishlaydigan kod.
"""
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    User yaratilganda yoki yangilanganda ishlaydi.
    Hozircha placeholder — keyinchalik AuditLog qo'shamiz.
    """
    if created:
        # TODO: AuditLog app qo'shilgach shu yerda log yoziladi
        pass


@receiver(user_logged_in)
def on_user_login(sender, request, user, **kwargs):
    """Login qilganda — IP va vaqtni saqlash uchun."""
    # TODO: AuditLog app qo'shilgach
    pass


@receiver(user_logged_out)
def on_user_logout(sender, request, user, **kwargs):
    """Logout qilganda."""
    # TODO: AuditLog app qo'shilgach
    pass
