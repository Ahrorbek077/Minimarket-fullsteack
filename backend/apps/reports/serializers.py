"""
Reports serializers — hisobot parametrlari va javob formatlari.
"""
from datetime import date, timedelta
from rest_framework import serializers


class DateRangeSerializer(serializers.Serializer):
    """Sana oralig'i — barcha hisobotlarda ishlatiladi."""
    date_from = serializers.DateField(required=False)
    date_to   = serializers.DateField(required=False)

    def validate(self, attrs):
        today    = date.today()
        d_from   = attrs.get("date_from", today.replace(day=1))
        d_to     = attrs.get("date_to",   today)

        if d_from > d_to:
            raise serializers.ValidationError(
                {"date_from": "Boshlanish sanasi tugash sanasidan katta bo'lmasligi kerak."}
            )
        if (d_to - d_from).days > 366:
            raise serializers.ValidationError(
                "Hisobot davri 1 yildan oshmasligi kerak."
            )
        attrs["date_from"] = d_from
        attrs["date_to"]   = d_to
        return attrs


class SalesSummarySerializer(serializers.Serializer):
    date_from      = serializers.DateField()
    date_to        = serializers.DateField()
    total_sales    = serializers.IntegerField()
    total_revenue  = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_discount = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_debt     = serializers.DecimalField(max_digits=18, decimal_places=2)
    cash_total     = serializers.DecimalField(max_digits=18, decimal_places=2)
    card_total     = serializers.DecimalField(max_digits=18, decimal_places=2)
    debt_total     = serializers.DecimalField(max_digits=18, decimal_places=2)
    gross_profit   = serializers.DecimalField(max_digits=18, decimal_places=2)
    profit_margin  = serializers.FloatField()


class PeriodSalesSerializer(serializers.Serializer):
    period  = serializers.DateField()
    count   = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=18, decimal_places=2)
    profit  = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)


class TopProductSerializer(serializers.Serializer):
    product__id         = serializers.IntegerField()
    product__name       = serializers.CharField()
    product__unit__short_name = serializers.CharField(allow_null=True)
    total_qty           = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_revenue       = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_profit        = serializers.DecimalField(max_digits=18, decimal_places=2)


class StockSummarySerializer(serializers.Serializer):
    total_items       = serializers.IntegerField()
    total_cost_value  = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_sell_value  = serializers.DecimalField(max_digits=18, decimal_places=2)
    potential_profit  = serializers.DecimalField(max_digits=18, decimal_places=2)
    low_stock_count   = serializers.IntegerField()
    out_of_stock      = serializers.IntegerField()


class ExportParamsSerializer(DateRangeSerializer):
    """Export uchun parametrlar."""
    file_format = serializers.ChoiceField(choices=["pdf", "excel"], default="excel")
    type    = serializers.ChoiceField(
        choices=["sales", "purchases", "stock", "top_products"],
        default="sales",
    )
    period  = serializers.ChoiceField(
        choices=["daily", "weekly", "monthly"],
        default="daily",
        required=False,
    )
    limit   = serializers.IntegerField(min_value=5, max_value=100, default=20, required=False)
