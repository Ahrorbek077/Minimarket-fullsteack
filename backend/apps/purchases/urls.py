from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import PurchaseViewSet

router = DefaultRouter()
router.register("", PurchaseViewSet, basename="purchases")

urlpatterns = [path("", include(router.urls))]
