"""
Reports views — APIView asosida.
"""
from django.http import HttpResponse, JsonResponse

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsAccountant, IsAdminOrAbove

from .export_view import _generate
from .querysets import (
    get_debt_report, get_purchases_report,
    get_sales_by_period, get_sales_report,
    get_sales_summary, get_stock_report,
    get_stock_summary, get_top_products,
)
from .serializers import (
    DateRangeSerializer, ExportParamsSerializer,
    PeriodSalesSerializer, SalesSummarySerializer,
    StockSummarySerializer, TopProductSerializer,
)


def _parse_dates(request):
    s = DateRangeSerializer(data=request.query_params)
    s.is_valid(raise_exception=True)
    return s.validated_data["date_from"], s.validated_data["date_to"]


# ─── Sales ────────────────────────────────────────────────────────────────────

class SalesSummaryView(APIView):
    permission_classes = [IsAccountant]

    @extend_schema(
        summary="Sotuvlar umumiy statistikasi", tags=["Reports"],
        parameters=[
            OpenApiParameter("date_from", str, description="2024-01-01"),
            OpenApiParameter("date_to",   str, description="2024-12-31"),
        ],
    )
    def get(self, request):
        d_from, d_to = _parse_dates(request)
        data = get_sales_summary(d_from, d_to)
        return Response({"success": True, "data": SalesSummarySerializer(data).data})


class SalesChartView(APIView):
    permission_classes = [IsAccountant]

    @extend_schema(
        summary="Sotuvlar grafigi (kun/hafta/oy)", tags=["Reports"],
        parameters=[
            OpenApiParameter("date_from", str),
            OpenApiParameter("date_to",   str),
            OpenApiParameter("period", str, description="daily|weekly|monthly"),
        ],
    )
    def get(self, request):
        d_from, d_to = _parse_dates(request)
        period = request.query_params.get("period", "daily")
        if period not in ("daily", "weekly", "monthly"):
            return Response(
                {"success": False, "error": {"message": "period: daily|weekly|monthly"}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = list(get_sales_by_period(d_from, d_to, period))
        return Response({"success": True, "data": PeriodSalesSerializer(data, many=True).data})


class TopProductsView(APIView):
    permission_classes = [IsAccountant]

    @extend_schema(
        summary="Eng ko'p sotilgan mahsulotlar", tags=["Reports"],
        parameters=[
            OpenApiParameter("date_from", str),
            OpenApiParameter("date_to",   str),
            OpenApiParameter("limit", int, description="5–100, default 20"),
        ],
    )
    def get(self, request):
        d_from, d_to = _parse_dates(request)
        limit = max(5, min(int(request.query_params.get("limit", 20)), 100))
        data  = list(get_top_products(d_from, d_to, limit))
        return Response({
            "success": True,
            "count":   len(data),
            "data":    TopProductSerializer(data, many=True).data,
        })


# ─── Stock ────────────────────────────────────────────────────────────────────

class StockSummaryView(APIView):
    permission_classes = [IsAccountant]

    @extend_schema(summary="Ombor umumiy holati", tags=["Reports"])
    def get(self, request):
        data = get_stock_summary()
        return Response({"success": True, "data": StockSummarySerializer(data).data})


# ─── Purchases ────────────────────────────────────────────────────────────────

class DebtReportView(APIView):
    permission_classes = [IsAccountant]

    @extend_schema(summary="Qarzlar hisoboti", tags=["Reports"])
    def get(self, request):
        qs = get_debt_report()
        data = [
            {
                "id":           p.pk,
                "company":      p.company.name,
                "total_amount": str(p.total_amount),
                "debt_amount":  str(p.debt_amount),
                "due_date":     str(p.due_date) if p.due_date else None,
                "is_overdue":   p.is_overdue,
                "status":       p.status,
            }
            for p in qs
        ]
        total_debt = sum(p.debt_amount for p in qs)
        return Response({
            "success":    True,
            "count":      len(data),
            "total_debt": str(total_debt),
            "data":       data,
        })


# ─── Export ───────────────────────────────────────────────────────────────────

class ExportReportView(APIView):
    """
    Export hisoboti — PDF yoki Excel.

    initial() override — content negotiation skip qilinadi,
    chunki view JSON emas, binary fayl qaytaradi.
    HttpResponse to'g'ridan-to'g'ri qaytariladi.
    """
    permission_classes = [IsAdminOrAbove]

    def initial(self, request, *args, **kwargs):
        """Authentication + permissions — renderer negotiation yo'q."""
        self.perform_authentication(request)
        self.check_permissions(request)
        self.check_throttles(request)

    @extend_schema(
        summary="Hisobotni PDF yoki Excel ga export", tags=["Reports"],
        parameters=[
            OpenApiParameter("file_format", str, description="pdf|excel"),
            OpenApiParameter("type",        str, description="sales|purchases|stock|top_products"),
            OpenApiParameter("date_from",   str),
            OpenApiParameter("date_to",     str),
            OpenApiParameter("limit",       int, description="Top mahsulotlar uchun (5–100)"),
        ],
    )
    def get(self, request):
        s = ExportParamsSerializer(data=request.query_params)
        if not s.is_valid():
            return JsonResponse(
                {"success": False, "error": {"message": str(s.errors)}},
                status=400,
            )

        params   = s.validated_data
        fmt      = params["file_format"]
        rpt_type = params["type"]
        d_from   = params["date_from"]
        d_to     = params["date_to"]

        ext      = "xlsx" if fmt == "excel" else "pdf"
        filename = f"{rpt_type}_report_{d_from}_{d_to}.{ext}"
        mime_map = {
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "pdf":   "application/pdf",
        }

        try:
            buf = _generate(fmt, rpt_type, d_from, d_to, params)
        except NotImplementedError as e:
            return JsonResponse(
                {"success": False, "error": {"message": str(e)}}, status=400
            )
        except Exception as e:
            return JsonResponse(
                {"success": False, "error": {"message": str(e)}}, status=500
            )

        resp = HttpResponse(buf.read(), content_type=mime_map[fmt])
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp
