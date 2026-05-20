"""
Products URL patterns.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, ProductViewSet, UnitViewSet

router = DefaultRouter()
router.register("units",      UnitViewSet,     basename="units")
router.register("categories", CategoryViewSet, basename="categories")
router.register("products",   ProductViewSet,  basename="products")

urlpatterns = [
    path("", include(router.urls)),
]
