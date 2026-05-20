from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LoginView, LogoutView, MeView, RefreshTokenView, UserViewSet

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")
router.register("me",    MeView,      basename="me")
router.register("",      LogoutView,  basename="auth")

urlpatterns = [
    path("login/",         LoginView.as_view(),        name="token_obtain_pair"),
    path("token/refresh/", RefreshTokenView.as_view(), name="token_refresh"),
    path("",               include(router.urls)),
]
