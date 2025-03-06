from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from io import BytesIO
from django.conf import settings
import os

def generate_pdf_ticket(event, user, booking):
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'tickets', f'{user.first_name}_{booking.id}.pdf')
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    style_heading = styles['Heading1']

    elements = []
    # Title
    elements.append(Paragraph("Event Ticket", style_heading))
    elements.append(Spacer(1, 12))
    
    # Event Details
    elements.append(Paragraph(f"<b>Event:</b> {event.title}", style_normal))
    if event.start_date and event.end_date:
        elements.append(Paragraph(f"<b>Date:</b> {event.start_date.strftime('%B %d, %Y, %I:%M %p')} - {event.end_date.strftime('%B %d, %Y, %I:%M %p')}", style_normal))
    elements.append(Paragraph(f"<b>Location:</b> {event.location}", style_normal))
    elements.append(Spacer(1, 12))
    
    # User Details
    elements.append(Paragraph(f"<b>Booked By:</b> {user.get_full_name()} ({user.email})", style_normal))
    elements.append(Spacer(1, 12))
    
    # Booking Details
    elements.append(Paragraph(f"<b>Booking ID:</b> {booking.id}", style_normal))
    elements.append(Paragraph(f"<b>Status:</b> {booking.booking_status}", style_normal))
    elements.append(Paragraph(f"<b>Tickets:</b> {booking.ticket_quantity}", style_normal))
    elements.append(Paragraph(f"<b>Total Price:</b> ₹{booking.total_price}", style_normal))
    elements.append(Spacer(1, 12))
    
    # Footer
    elements.append(Paragraph("Thank you for your booking! Please bring this ticket to the event.", style_normal))
    
    doc.build(elements)
    return pdf_path