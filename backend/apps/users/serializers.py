"""
User serializers.
"""
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer as BaseTokenSerializer

from .models import User, UserRole, UserLanguage


class TokenObtainPairSerializer(BaseTokenSerializer):
    """
    JWT token serializer — user ma'lumotlarini ham qaytaradi.
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserMeSerializer(self.user).data
        return data


class UserListSerializer(serializers.ModelSerializer):
    """Ro'yxat uchun qisqa serializer."""

    class Meta:
        model = User
        fields = [
            "id", "email", "full_name", "phone",
            "role", "is_active", "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]


class UserDetailSerializer(serializers.ModelSerializer):
    """To'liq user ma'lumoti."""
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    language_display = serializers.CharField(source="get_language_display", read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "email", "full_name", "phone", "avatar",
            "role", "role_display", "language", "language_display",
            "is_active", "date_joined", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "date_joined", "created_at", "updated_at"]


class UserCreateSerializer(serializers.ModelSerializer):
    """Yangi user yaratish."""
    password = serializers.CharField(
        write_only=True, required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True, required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = [
            "email", "full_name", "phone",
            "role", "language",
            "password", "password_confirm",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Parollar mos kelmadi."}
            )
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):
    """User ma'lumotlarini yangilash (admin uchun)."""

    class Meta:
        model = User
        fields = ["full_name", "phone", "role", "language", "is_active"]


class UserMeSerializer(serializers.ModelSerializer):
    """O'z profilini ko'rish."""
    role_display    = serializers.CharField(source="get_role_display", read_only=True)
    language_display = serializers.CharField(source="get_language_display", read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "email", "full_name", "phone", "avatar",
            "role", "role_display", "language", "language_display",
            "date_joined",
        ]
        read_only_fields = ["id", "email", "role", "date_joined"]


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """O'z profilini tahrirlash."""

    class Meta:
        model = User
        fields = ["full_name", "phone", "avatar", "language"]


class ChangePasswordSerializer(serializers.Serializer):
    """Parol almashtirish."""
    old_password  = serializers.CharField(
        required=True, write_only=True,
        style={"input_type": "password"},
    )
    new_password  = serializers.CharField(
        required=True, write_only=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    new_password_confirm = serializers.CharField(
        required=True, write_only=True,
        style={"input_type": "password"},
    )

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Eski parol noto'g'ri.")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "Yangi parollar mos kelmadi."}
            )
        return attrs
