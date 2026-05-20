"""
Export helper funksiyalar — views.py da ishlatiladi.
Bu modul faqat _generate() funksiyasini eksport qiladi.
ExportReportView → reports/views.py da.
"""
from .querysets import (
    get_sales_report, get_sales_summary,
    get_purchases_report, get_stock_report,
    get_stock_summary, get_top_products,
)


def _generate(fmt: str, rpt_type: str, d_from, d_to, params: dict):
    """
    Hisobot turini aniqlash va BytesIO buffer qaytarish.
    fmt:      'excel' | 'pdf'
    rpt_type: 'sales' | 'purchases' | 'stock' | 'top_products'
    """
    from .excel import (
        export_purchases_excel, export_sales_excel,
        export_stock_excel, export_top_products_excel,
    )
    from .pdf import export_purchases_pdf, export_sales_pdf, export_stock_pdf

    if rpt_type == "sales":
        summary = get_sales_summary(d_from, d_to)
        qs      = get_sales_report(d_from, d_to)
        return (
            export_sales_excel(qs, d_from, d_to, summary)
            if fmt == "excel"
            else export_sales_pdf(qs, d_from, d_to, summary)
        )

    elif rpt_type == "purchases":
        qs = get_purchases_report(d_from, d_to)
        return (
            export_purchases_excel(qs, d_from, d_to)
            if fmt == "excel"
            else export_purchases_pdf(qs, d_from, d_to)
        )

    elif rpt_type == "stock":
        qs      = get_stock_report()
        summary = get_stock_summary()
        return (
            export_stock_excel(qs, summary)
            if fmt == "excel"
            else export_stock_pdf(qs, summary)
        )

    elif rpt_type == "top_products":
        limit = params.get("limit", 20)
        data  = list(get_top_products(d_from, d_to, limit))
        if fmt == "excel":
            return export_top_products_excel(data, d_from, d_to)
        raise NotImplementedError("Top products PDF hali ishlanmoqda.")

    raise ValueError(f"Noma'lum hisobot turi: {rpt_type}")
