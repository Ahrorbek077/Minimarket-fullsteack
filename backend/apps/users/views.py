"""
User views — faqat HTTP handling, logika services.py da.
"""
from django.conf import settings
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.mixins import SoftDeleteMixin
from core.permissions import IsAdminOrAbove, IsSuperAdmin

from .models import User
from .serializers import (
    ChangePasswordSerializer,
    ProfileUpdateSerializer,
    TokenObtainPairSerializer,
    UserCreateSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserMeSerializer,
    UserUpdateSerializer,
)
from .services import UserService

# ─── Cookie helpers ───────────────────────────────────────────────────────────

_COOKIE_NAME    = "refresh_token"
_COOKIE_MAX_AGE = 60 * 60 * 24 * 7   # 7 kun


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    """refresh_token ni httpOnly cookie ga yozadi — XSS dan himoyalangan."""
    response.set_cookie(
        key=_COOKIE_NAME,
        value=refresh_token,
        max_age=_COOKIE_MAX_AGE,
        httponly=True,
        secure=not settings.DEBUG,   # production da HTTPS only
        samesite="Lax",
        path="/api/v1/auth/",
    )


def _delete_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=_COOKIE_NAME, path="/api/v1/auth/")


# ─── Auth Views ───────────────────────────────────────────────────────────────

@extend_schema(tags=["Auth"])
class LoginView(TokenObtainPairView):
    """
    Login — access_token body da, refresh_token httpOnly cookie da.
    """
    serializer_class   = TokenObtainPairSerializer
    permission_classes = [AllowAny]
    throttle_classes   = []   # LoginRateThrottle qo'shiladi quyida

    def get_throttles(self):
        from core.permissions import LoginRateThrottle
        return [LoginRateThrottle()]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            refresh = response.data.pop("refresh", None)
            if refresh:
                _set_refresh_cookie(response, refresh)
        return response


@extend_schema(tags=["Auth"])
class RefreshTokenView(TokenRefreshView):
    """
    Yangi access token — refresh_token cookie dan o'qiladi.
    """
    def post(self, request, *args, **kwargs):
        if _COOKIE_NAME in request.COOKIES and "refresh" not in request.data:
            data            = request.data.copy()
            data["refresh"] = request.COOKIES[_COOKIE_NAME]
            request._full_data = data
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            new_refresh = response.data.pop("refresh", None)
            if new_refresh:
                _set_refresh_cookie(response, new_refresh)
        return response


@extend_schema(tags=["Auth"])
class LogoutView(viewsets.ViewSet):
    """Logout — cookie o'chiriladi + token blacklist."""
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"])
    def logout(self, request):
        from rest_framework_simplejwt.tokens import RefreshToken
        from rest_framework_simplejwt.exceptions import TokenError
        refresh = (
            request.COOKIES.get(_COOKIE_NAME)
            or request.data.get("refresh")
        )
        if refresh:
            try:
                RefreshToken(refresh).blacklist()
            except TokenError:
                pass
        resp = Response({"success": True, "message": "Tizimdan chiqildi."})
        _delete_refresh_cookie(resp)
        return resp


# ─── User ViewSet ─────────────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(summary="Barcha userlar ro'yxati", tags=["Users"]),
    create=extend_schema(summary="Yangi user yaratish", tags=["Users"]),
    retrieve=extend_schema(summary="User ma'lumoti", tags=["Users"]),
    update=extend_schema(summary="Userni yangilash", tags=["Users"]),
    partial_update=extend_schema(summary="Userni qisman yangilash", tags=["Users"]),
    destroy=extend_schema(summary="Userni o'chirish (soft)", tags=["Users"]),
)
class UserViewSet(SoftDeleteMixin, viewsets.ModelViewSet):
    """User CRUD — faqat Admin va Super Admin."""
    queryset           = User.all_objects.filter(deleted_at__isnull=True).order_by("-date_joined")
    permission_classes = [IsAdminOrAbove]

    def get_serializer_class(self):
        if self.action == "create":            return UserCreateSerializer
        if self.action in ("update", "partial_update"): return UserUpdateSerializer
        if self.action == "retrieve":          return UserDetailSerializer
        return UserListSerializer

    def get_queryset(self):
        qs = User.all_objects.filter(deleted_at__isnull=True).order_by("-date_joined")
        if not self.request.user.is_super_admin:
            from .models import UserRole
            qs = qs.exclude(role=UserRole.SUPER_ADMIN)
        search = self.request.query_params.get("search")
        if search:
            from django.db.models import Q
            qs = qs.filter(Q(full_name__icontains=search) | Q(email__icontains=search))
        role = self.request.query_params.get("role")
        if role:
            qs = qs.filter(role=role)
        return qs

    def perform_destroy(self, instance):
        UserService.soft_delete_user(instance)

    @extend_schema(summary="Parolni reset qilish", tags=["Users"])
    @action(detail=True, methods=["post"], permission_classes=[IsSuperAdmin], url_path="reset-password")
    def reset_password(self, request, pk=None):
        user         = self.get_object()
        new_password = request.data.get("new_password")
        if not new_password:
            return Response(
                {"success": False, "error": {"message": "new_password majburiy."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        UserService.change_password(user, new_password)
        return Response({"success": True, "message": "Parol o'zgartirildi."})


# ─── Profile Views ────────────────────────────────────────────────────────────

class MeView(viewsets.ViewSet):
    """O'z profilini boshqarish."""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="O'z profili", tags=["Profile"])
    @action(detail=False, methods=["get"])
    def profile(self, request):
        return Response({"success": True, "data": UserMeSerializer(request.user).data})

    @extend_schema(summary="Profilni tahrirlash", tags=["Profile"])
    @action(detail=False, methods=["patch"])
    def update_profile(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "success": True,
            "message": "Profil yangilandi.",
            "data":    UserMeSerializer(request.user).data,
        })

    @extend_schema(summary="Parol almashtirish", tags=["Profile"])
    @action(detail=False, methods=["post"], url_path="change-password")
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        UserService.change_password(request.user, serializer.validated_data["new_password"])
        return Response({"success": True, "message": "Parol muvaffaqiyatli o'zgartirildi."})
