"""
Custom exception handler — barcha xatolar bir xil formatda.
"""
from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    DRF default handler ustiga qo'shimcha format.

    Response format:
    {
        "success": false,
        "error": {
            "code": "not_found",
            "message": "Not found.",
            "details": {...}  # optional
        }
    }
    """
    # Django exceptionlarini DRF ga o'girish
    if isinstance(exc, Http404):
        from rest_framework.exceptions import NotFound
        exc = NotFound()
    elif isinstance(exc, PermissionDenied):
        from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied
        exc = DRFPermissionDenied()

    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            "success": False,
            "error": {
                "code": _get_error_code(exc),
                "message": _get_error_message(response.data),
                "details": _get_error_details(response.data),
            }
        }
        response.data = error_data

    return response


def _get_error_code(exc) -> str:
    if hasattr(exc, "default_code"):
        return exc.default_code
    return "error"


def _get_error_message(data) -> str:
    if isinstance(data, dict):
        if "detail" in data:
            return str(data["detail"])
        # Birinchi field xatosi
        for key, value in data.items():
            if isinstance(value, list) and value:
                return f"{key}: {value[0]}"
        return "Xato yuz berdi."
    if isinstance(data, list) and data:
        return str(data[0])
    return str(data)


def _get_error_details(data) -> dict | None:
    if isinstance(data, dict) and "detail" not in data:
        return data
    return None


class BusinessLogicError(APIException):
    """Biznes mantiq xatosi — 400."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "business_logic_error"

    def __init__(self, message: str, code: str = None):
        self.default_code = code or self.default_code
        super().__init__(detail=message)


class InsufficientStockError(BusinessLogicError):
    """Omborida yetarli mahsulot yo'q."""
    default_code = "insufficient_stock"


class InvalidPaymentError(BusinessLogicError):
    """To'lov xatosi."""
    default_code = "invalid_payment"
