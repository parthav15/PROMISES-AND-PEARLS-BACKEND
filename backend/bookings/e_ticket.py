import os
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
)
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_RIGHT
from reportlab.pdfgen import canvas

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(
    TTFont(
        'Poppins',
        os.path.join(settings.STATIC_ROOT, 'fonts/Poppins/Poppins-Bold.ttf')
    )
)
pdfmetrics.registerFont(
    TTFont(
        'Merriweather',
        os.path.join(
            settings.STATIC_ROOT,
            'fonts/Merriweather/Merriweather-Italic-VariableFont_opsz,wdth,wght.ttf'
        )
    )
)

def generate_pdf_ticket(event, booking, ticket):
    page_width = 8.5 * inch
    page_height = 3.5 * inch

    pdf_name = f'{ticket.attendee["firstName"]}_{event.title}_{event.start_date.strftime("%d%B%Y")}.pdf'
    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'tickets')
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, pdf_name)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=(page_width, page_height),
        rightMargin=0.15 * inch,
        leftMargin=0.15 * inch,
        topMargin=0.15 * inch,
        bottomMargin=0.15 * inch
    )

    background_image_path = os.path.join(settings.STATIC_ROOT, "images", "ticket_splash_bg.png")

    def draw_ticket_background(canv, doc_template):
        canv.saveState()
        canv.drawImage(
            background_image_path,
            0,
            0,
            width=page_width,
            height=page_height,
            preserveAspectRatio=True
        )
        canv.restoreState()

    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle(
        name='Normal',
        fontName='Merriweather',
        fontSize=7,
        leading=8,
        wordWrap='CJK'
    )

    subheading_style = ParagraphStyle(
        name='Subheading',
        parent=normal_style,
        fontName='Poppins',
        fontSize=7,
        textColor=colors.black
    )

    def split_text(text, max_length=40):
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            if len(current_line) + len(word) < max_length:
                current_line += " " + word
            else:
                lines.append(current_line.strip())
                current_line = word

        if current_line:
            lines.append(current_line.strip())

        return "<br/>".join(lines)

    left_column = []

    company_title_style = ParagraphStyle(
        name='CompanyTitleStyle',
        fontName='Poppins',
        fontSize=14,
        textColor=colors.purple,
        spaceAfter=6
    )

    event_title_style = ParagraphStyle(
        "EventTitleStyle",
        fontName="Poppins",
        fontSize=14,
        textColor="black",
        spaceAfter=6
    )

    location_style = ParagraphStyle(
        "EventLocationStyle",
        fontName="Merriweather",
        fontSize=10,
        textColor="black",
    )

    left_column.append(Paragraph("Promises and Pearls", company_title_style))
    left_column.append(Spacer(1, 0.5))

    event_title = event.title or "Event Name"
    location_str = event.location or "Event Venue"

    formatted_title = split_text(event_title)
    formatted_location = split_text(location_str)

    left_column.append(Paragraph(formatted_title, event_title_style))
    left_column.append(Spacer(1, 0.5))
    left_column.append(Paragraph(formatted_location, location_style))
    left_column.append(Spacer(1, 2))

    if event.start_date:
        date_str = event.start_date.strftime("%m.%d.%Y | %I:%M %p")
        left_column.append(Paragraph(date_str, subheading_style))
        left_column.append(Spacer(1, 2))

    left_column.append(Paragraph(f"N {ticket.ticket_id}", subheading_style))
    left_column.append(Spacer(1, 2))

    right_subtable_data = []

    price_style = ParagraphStyle(
        name='PriceStyle',
        fontName='Poppins',
        fontSize=12,
        textColor=colors.black,
        alignment=TA_RIGHT
    )

    price_value = f"INR {booking.total_price:.2f}"
    price_paragraph = Paragraph(price_value, price_style)

    qr_flowables = []
    if ticket.qr_code:
        qr_img = Image(ticket.qr_code.path, width=1.0 * inch, height=1.0 * inch)
        qr_flowables.append(qr_img)

    right_subtable_data.append([price_paragraph])
    if qr_flowables:
        right_subtable_data.append([qr_flowables])

    right_subtable = Table(right_subtable_data, colWidths=[2.8 * inch])
    right_subtable.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,0), 'RIGHT'),
        ('ALIGN', (0,1), (-1,1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))

    right_column = [right_subtable]

    max_row_height = 215
    col_width_left = 5.2 * inch
    col_width_right = 3.0 * inch
    row_height = min(max_row_height, page_height - (doc.topMargin + doc.bottomMargin))

    table_data = [
        [left_column, right_column]
    ]

    ticket_table = Table(
        table_data,
        colWidths=[col_width_left, col_width_right],
        rowHeights=[row_height]
    )

    ticket_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LINEAFTER', (0,0), (0,-1), 1, colors.black, None, (2,2)),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('FONTSIZE', (0,0), (-1,-1), 7),
    ]))

    elements = [ticket_table]

    doc.build(
        elements,
        onFirstPage=draw_ticket_background,
        onLaterPages=draw_ticket_background
    )

    return pdf_path
