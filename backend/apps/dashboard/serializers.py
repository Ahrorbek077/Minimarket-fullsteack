"""
Dashboard serializers.
"""
from rest_framework import serializers


class PeriodStatsSerializer(serializers.Serializer):
    period      = serializers.CharField()
    date_from   = serializers.DateField()
    date_to     = serializers.DateField()
    sales_count = serializers.IntegerField()
    revenue     = serializers.DecimalField(max_digits=18, decimal_places=2)
    discount    = serializers.DecimalField(max_digits=18, decimal_places=2)
    gross_profit= serializers.DecimalField(max_digits=18, decimal_places=2)
    debt        = serializers.DecimalField(max_digits=18, decimal_places=2)
    cash        = serializers.DecimalField(max_digits=18, decimal_places=2)
    card        = serializers.DecimalField(max_digits=18, decimal_places=2)
    debt_payments = serializers.DecimalField(max_digits=18, decimal_places=2)


class StockOverviewSerializer(serializers.Serializer):
    total_products  = serializers.IntegerField()
    low_stock_count = serializers.IntegerField()
    out_of_stock    = serializers.IntegerField()
    cost_value      = serializers.DecimalField(max_digits=18, decimal_places=2)
    sell_value      = serializers.DecimalField(max_digits=18, decimal_places=2)


class DebtsOverviewSerializer(serializers.Serializer):
    count         = serializers.IntegerField()
    total_debt    = serializers.DecimalField(max_digits=18, decimal_places=2)
    overdue_count = serializers.IntegerField()
    overdue_debt  = serializers.DecimalField(max_digits=18, decimal_places=2)


class TopProductSerializer(serializers.Serializer):
    product__id    = serializers.IntegerField()
    product__name  = serializers.CharField()
    total_qty      = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_revenue  = serializers.DecimalField(max_digits=18, decimal_places=2)


class SalesChartSerializer(serializers.Serializer):
    date    = serializers.DateField()
    count   = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=18, decimal_places=2)


class RecentSaleSerializer(serializers.Serializer):
    id              = serializers.IntegerField()
    invoice_no      = serializers.CharField()
    net_amount      = serializers.DecimalField(max_digits=18, decimal_places=2)
    created_at      = serializers.DateTimeField()
    cashier__full_name = serializers.CharField(allow_null=True)


class LowStockAlertSerializer(serializers.Serializer):
    product__id         = serializers.IntegerField()
    product__name       = serializers.CharField()
    product__unit__short_name = serializers.CharField(allow_null=True)
    quantity            = serializers.DecimalField(max_digits=12, decimal_places=2)
    product__min_stock  = serializers.DecimalField(max_digits=12, decimal_places=2)


class DashboardSerializer(serializers.Serializer):
    """Barcha dashboard ma'lumotlari bitta javobda."""
    today        = PeriodStatsSerializer()
    week         = PeriodStatsSerializer()
    month        = PeriodStatsSerializer()
    year         = PeriodStatsSerializer()
    stock        = StockOverviewSerializer()
    debts        = DebtsOverviewSerializer()
    top_products = TopProductSerializer(many=True)
    sales_chart  = SalesChartSerializer(many=True)
    recent_sales = RecentSaleSerializer(many=True)
    low_stock    = LowStockAlertSerializer(many=True)
