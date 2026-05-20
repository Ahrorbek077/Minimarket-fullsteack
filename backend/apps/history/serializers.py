"""
History serializers.
"""
from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user_name      = serializers.CharField(
        source="user.full_name", read_only=True, default="Tizim"
    )
    user_email     = serializers.CharField(
        source="user.email",     read_only=True, default=None
    )
    action_display = serializers.CharField(
        source="get_action_display", read_only=True
    )

    class Meta:
        model  = AuditLog
        fields = [
            "id",
            "user", "user_name", "user_email",
            "action", "action_display",
            "model_name", "object_id", "object_repr",
            "changes", "ip_address", "extra",
            "created_at",
        ]
        read_only_fields = fields
