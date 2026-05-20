"""
PDF export — reportlab bilan.
"""
import io
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
)

# ─── Styles ───────────────────────────────────────────────────────────────────

BRAND_BLUE  = colors.HexColor("#1F4E79")
LIGHT_BLUE  = colors.HexColor("#D6E4F0")
ALT_ROW     = colors.HexColor("#EBF3FB")
WHITE       = colors.white
DARK_GRAY   = colors.HexColor("#333333")

styles = getSampleStyleSheet()

TITLE_STYLE = ParagraphStyle(
    "Title",
    fontSize=16, fontName="Helvetica-Bold",
    textColor=BRAND_BLUE, spaceAfter=4,
)
SUBTITLE_STYLE = ParagraphStyle(
    "Subtitle",
    fontSize=10, fontName="Helvetica",
    textColor=colors.gray, spaceAfter=12,
)
NORMAL_STYLE = ParagraphStyle(
    "Normal", fontSize=9, fontName="Helvetica"
)


def _base_table_style(has_total=True, data_len=0) -> list:
    style = [
        # Header
        ("BACKGROUND",   (0, 0), (-1, 0), BRAND_BLUE),
        ("TEXTCOLOR",    (0, 0), (-1, 0), WHITE),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0), 9),
        ("ALIGN",        (0, 0), (-1, 0), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2 if has_total else -1),
         [WHITE, ALT_ROW]),
        ("FONTSIZE",     (0, 1), (-1, -1), 8),
        ("FONTNAME",     (0, 1), (-1, -1), "Helvetica"),
        ("GRID",         (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ("LEFTPADDING",  (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    if has_total and data_len:
        # Oxirgi qator — jami
        style += [
            ("BACKGROUND", (0, -1), (-1, -1), LIGHT_BLUE),
            ("FONTNAME",   (0, -1), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE",   (0, -1), (-1, -1), 9),
        ]
    return style


def _make_doc(buf, landscape_mode=False) -> SimpleDocTemplate:
    pagesize = landscape(A4) if landscape_mode else A4
    return SimpleDocTemplate(
        buf,
        pagesize=pagesize,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm,   bottomMargin=1.5*cm,
    )


def _header_elements(title: str, subtitle: str = "") -> list:
    elems = [Paragraph(title, TITLE_STYLE)]
    if subtitle:
        elems.append(Paragraph(subtitle, SUBTITLE_STYLE))
    elems.append(Spacer(1, 0.3*cm))
    return elems


def _to_buffer(doc, story) -> io.BytesIO:
    buf = io.BytesIO()
    doc.filename = buf
    doc.build(story)
    buf.seek(0)
    return buf


# ─── Sales PDF ─────────────────────────────────────────────────────────────────

def export_sales_pdf(sales_qs, date_from, date_to, summary: dict) -> io.BytesIO:
    buf = io.BytesIO()
    doc = _make_doc(buf, landscape_mode=True)
    story = _header_elements(
        "Sotuvlar hisoboti",
        f"Davr: {date_from} — {date_to}  |  "
        f"Jami: {summary['total_sales']} ta sotuv  |  "
        f"Tushum: {summary['total_revenue']:,.0f} so'm"
    )

    from sales.models import PaymentMethod
    headers = ["№", "Chek", "Sana", "Kassir",
               "Jami", "Chegirma", "To'lanadigan",
               "Naqd", "Karta", "Nasiya", "Holat"]
    col_widths = [1*cm, 3.5*cm, 2.8*cm, 3.5*cm,
                  2.8*cm, 2.5*cm, 2.8*cm,
                  2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm]

    data = [headers]
    for idx, sale in enumerate(sales_qs, 1):
        cash = sum(p.amount for p in sale.payments.all() if p.method == PaymentMethod.CASH)
        card = sum(p.amount for p in sale.payments.all() if p.method == PaymentMethod.CARD)
        debt = sum(p.amount for p in sale.payments.all() if p.method == PaymentMethod.DEBT)
        data.append([
            str(idx),
            sale.invoice_no,
            sale.created_at.strftime("%d.%m.%Y"),
            sale.cashier.full_name if sale.cashier else "—",
            f"{sale.total_amount:,.0f}",
            f"{sale.discount_amount:,.0f}",
            f"{sale.net_amount:,.0f}",
            f"{cash:,.0f}",
            f"{card:,.0f}",
            f"{debt:,.0f}",
            sale.get_status_display(),
        ])

    data.append([
        "JAMI", "", "", f"{summary['total_sales']} ta",
        f"{summary['total_revenue']:,.0f}",
        f"{summary['total_discount']:,.0f}",
        f"{summary['total_revenue']:,.0f}",
        f"{summary['cash_total']:,.0f}",
        f"{summary['card_total']:,.0f}",
        f"{summary['debt_total']:,.0f}",
        "",
    ])

    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle(_base_table_style(has_total=True, data_len=len(data))))
    story.append(t)

    # Xulosa qutisi
    story.append(Spacer(1, 0.5*cm))
    summary_data = [
        ["Ko'rsatkich", "Qiymat"],
        ["Brutto foyda", f"{summary['gross_profit']:,.0f} so'm"],
        ["Foyda margin", f"{summary['profit_margin']} %"],
        ["Jami chegirma", f"{summary['total_discount']:,.0f} so'm"],
        ["Nasiya qoldig'i", f"{summary['total_debt']:,.0f} so'm"],
    ]
    st = Table(summary_data, colWidths=[5*cm, 5*cm])
    st.setStyle(TableStyle(_base_table_style(has_total=False)))
    story.append(st)

    doc.build(story)
    buf.seek(0)
    return buf


# ─── Stock PDF ─────────────────────────────────────────────────────────────────

def export_stock_pdf(stock_qs, summary: dict) -> io.BytesIO:
    buf = io.BytesIO()
    doc = _make_doc(buf, landscape_mode=True)
    story = _header_elements(
        "Ombor holati hisoboti",
        f"Jami: {summary['total_items']} ta mahsulot  |  "
        f"Ombor qiymati: {summary['total_cost_value']:,.0f} so'm"
    )

    headers = ["№", "Mahsulot", "Kat.", "Birlik", "Qoldiq",
               "Min", "Holat", "Tan narxi", "Sotish narxi",
               "Tan qiymati", "Sotuv qiymati"]
    col_widths = [0.8*cm, 5*cm, 2.5*cm, 1.5*cm, 1.8*cm,
                  1.8*cm, 2*cm, 2.5*cm, 2.5*cm, 3*cm, 3*cm]

    data = [headers]
    for idx, stock in enumerate(stock_qs, 1):
        p      = stock.product
        is_low = stock.quantity <= p.min_stock
        status = "Kam" if is_low else ("Tugagan" if stock.quantity <= 0 else "Yetarli")
        data.append([
            str(idx),
            p.name[:35],
            p.category.name[:12] if p.category else "—",
            p.unit.short_name if p.unit else "—",
            f"{stock.quantity:,.2f}",
            f"{p.min_stock:,.2f}",
            status,
            f"{p.cost_price:,.0f}",
            f"{p.sell_price:,.0f}",
            f"{stock.quantity * p.cost_price:,.0f}",
            f"{stock.quantity * p.sell_price:,.0f}",
        ])

    data.append([
        "JAMI", f"{summary['total_items']} ta", "", "", "", "", "", "", "",
        f"{summary['total_cost_value']:,.0f}",
        f"{summary['total_sell_value']:,.0f}",
    ])

    ts = _base_table_style(has_total=True, data_len=len(data))
    # Kam qoldiq — sariq rang
    for row_idx, stock in enumerate(stock_qs, 1):
        if stock.quantity <= stock.product.min_stock:
            ts.append(("BACKGROUND", (6, row_idx), (6, row_idx), colors.HexColor("#FFF3CD")))
            ts.append(("TEXTCOLOR",  (6, row_idx), (6, row_idx), colors.HexColor("#856404")))

    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle(ts))
    story.append(t)
    doc.build(story)
    buf.seek(0)
    return buf


# ─── Purchases PDF ─────────────────────────────────────────────────────────────

def export_purchases_pdf(purchases_qs, date_from, date_to) -> io.BytesIO:
    buf = io.BytesIO()
    doc = _make_doc(buf, landscape_mode=True)
    story = _header_elements(
        "Xaridlar hisoboti", f"Davr: {date_from} — {date_to}"
    )

    headers = ["№", "Kompaniya", "Filial", "Hisob-f.", "Sana",
               "Jami summa", "To'landi", "Qarz", "Muddat", "Holat"]
    col_widths = [0.8*cm, 4.5*cm, 3.5*cm, 3*cm, 2.5*cm,
                  3*cm, 3*cm, 3*cm, 2.5*cm, 2.5*cm]

    data    = [headers]
    t_sum   = Decimal("0")
    t_debt  = Decimal("0")
    for idx, p in enumerate(purchases_qs, 1):
        data.append([
            str(idx),
            p.company.name[:25],
            p.branch.name[:18] if p.branch else "—",
            p.invoice_no or "—",
            p.created_at.strftime("%d.%m.%Y"),
            f"{p.total_amount:,.0f}",
            f"{p.paid_amount:,.0f}",
            f"{p.debt_amount:,.0f}",
            str(p.due_date) if p.due_date else "—",
            p.get_status_display(),
        ])
        t_sum  += p.total_amount
        t_debt += p.debt_amount

    data.append(["JAMI", "", "", "", "",
                 f"{t_sum:,.0f}", "", f"{t_debt:,.0f}", "", ""])

    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle(_base_table_style(has_total=True, data_len=len(data))))
    story.append(t)
    doc.build(story)
    buf.seek(0)
    return buf
