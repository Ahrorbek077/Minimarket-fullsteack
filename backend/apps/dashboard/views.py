"""
Dashboard views.
"""
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsAccountant, IsCashier

from .querysets import (
    get_debts_overview,
    get_low_stock_alerts,
    get_period_stats,
    get_recent_sales,
    get_sales_chart,
    get_stock_overview,
    get_top_products_today,
)
from .serializers import DashboardSerializer, PeriodStatsSerializer


class DashboardView(APIView):
    """
    Asosiy dashboard — bitta so'rovda barcha ma'lumotlar.
    Frontend bitta API chaqiradi, hammasi tayyor.
    """
    permission_classes = [IsCashier]

    @extend_schema(
        summary="Dashboard — barcha statistika",
        tags=["Dashboard"],
        parameters=[
            OpenApiParameter(
                "chart_days", int,
                description="Grafik uchun necha kun (default 7, max 30)",
            ),
            OpenApiParameter(
                "top_limit", int,
                description="Top mahsulotlar soni (default 5)",
            ),
        ],
        responses={200: DashboardSerializer},
    )
    def get(self, request):
        chart_days = min(int(request.query_params.get("chart_days", 7)), 30)
        top_limit  = min(int(request.query_params.get("top_limit",  5)), 20)

        data = {
            "today":        get_period_stats("today"),
            "week":         get_period_stats("week"),
            "month":        get_period_stats("month"),
            "year":         get_period_stats("year"),
            "stock":        get_stock_overview(),
            "debts":        get_debts_overview(),
            "top_products": get_top_products_today(top_limit),
            "sales_chart":  get_sales_chart(chart_days),
            "recent_sales": get_recent_sales(5),
            "low_stock":    get_low_stock_alerts(5),
        }

        serializer = DashboardSerializer(data)
        return Response({"success": True, "data": serializer.data})


class PeriodStatsView(APIView):
    """
    Alohida davr statistikasi — frontend widget uchun.
    ?period=today | week | month | year
    """
    permission_classes = [IsCashier]

    @extend_schema(
        summary="Davr statistikasi",
        tags=["Dashboard"],
        parameters=[
            OpenApiParameter(
                "period", str,
                description="today | week | month | year",
            ),
        ],
        responses={200: PeriodStatsSerializer},
    )
    def get(self, request):
        period = request.query_params.get("period", "today")
        if period not in ("today", "week", "month", "year"):
            return Response(
                {"success": False, "error": {
                    "message": "period: today | week | month | year"
                }},
                status=400,
            )
        data = get_period_stats(period)
        return Response({"success": True, "data": PeriodStatsSerializer(data).data})
