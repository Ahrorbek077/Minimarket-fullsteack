from django.urls import path
from .views import DashboardView, PeriodStatsView

urlpatterns = [
    path("",        DashboardView.as_view(),     name="dashboard"),
    path("period/", PeriodStatsView.as_view(),   name="dashboard-period"),
]
