from django.urls import path
from .views import (
    SalesSummaryView, SalesChartView, TopProductsView,
    StockSummaryView, DebtReportView, ExportReportView,
)

urlpatterns = [
    path("sales/summary/",      SalesSummaryView.as_view(),  name="reports-sales-summary"),
    path("sales/chart/",        SalesChartView.as_view(),    name="reports-sales-chart"),
    path("sales/top-products/", TopProductsView.as_view(),   name="reports-top-products"),
    path("stock/summary/",      StockSummaryView.as_view(),  name="reports-stock-summary"),
    path("purchases/debts/",    DebtReportView.as_view(),    name="reports-debt-report"),
    path("export/",             ExportReportView.as_view(),  name="reports-export"),
]
