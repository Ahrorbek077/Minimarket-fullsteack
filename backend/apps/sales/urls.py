from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, SaleViewSet

router = DefaultRouter()
router.register("cart",  CartViewSet, basename="cart")
router.register("",      SaleViewSet, basename="sales")

urlpatterns = [path("", include(router.urls))]
