"""
ViewSet mixinlari — takroriy koddan qochish uchun.
"""
from rest_framework.response import Response
from rest_framework import status


class SoftDeleteMixin:
    """
    ViewSet uchun soft delete mixin.
    destroy() → perform_destroy() orqali ishlaydi.
    perform_destroy() ni override qilib custom logika yozish mumkin.
    """
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"success": True, "message": "Muvaffaqiyatli o'chirildi."},
            status=status.HTTP_200_OK
        )

    def perform_destroy(self, instance):
        """Default — BaseModel.delete() (soft delete) chaqiradi."""
        instance.delete()


class SuccessResponseMixin:
    """Muvaffaqiyatli javob uchun standart format."""

    @staticmethod
    def success_response(data=None, message="Muvaffaqiyatli.", status_code=status.HTTP_200_OK):
        return Response(
            {"success": True, "message": message, "data": data},
            status=status_code
        )
