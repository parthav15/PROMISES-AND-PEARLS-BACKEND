from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings

from bookings.models import Booking
from events.models import Event
from users.models import CustomUser

from users.utils import jwt_decode, auth_user

import json

from bookings.e_ticket import generate_pdf_ticket

from django.core.mail import EmailMessage

@csrf_exempt
@require_http_methods(["POST"])
def create_booking(request):
    try:
        try:
            bearer = request.headers.get('Authorization')
            if not bearer:
                return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
            
            token = bearer.split()[1]
            if not auth_user(token):
                return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
            
            try:
                email = jwt_decode(token)['email']
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)
            except KeyError:
                return JsonResponse({'success': False, 'message': 'Invalid token format.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Unexpected error: {str(e)}'}, status=500)
        
        data = json.loads(request.body)

        event_id = data.get('event_id')
        ticket_quantity = data.get('ticket_quantity', 1)

        event = Event.objects.get(id=event_id)

        booking = Booking.objects.create(
            event=event,
            user=user,
            ticket_quantity=ticket_quantity,
            total_price=event.event_price * ticket_quantity,
            booking_status=Booking.STATUS_PENDING
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Booking created successfully',
            'data': {
                'id': booking.id,
                'event': booking.event.title,
                'user': booking.user.email,
                'ticket_quantity': booking.ticket_quantity,
                'total_price': str(booking.total_price),
                'booking_status': booking.booking_status
            }
        }, status=201)

    except Event.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Event not found.'}, status=404)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

def send_ticket(event, user, booking):
    try:
        pdf_path = generate_pdf_ticket(event, user, booking)
    except Exception as e:
        print(f"Error generating pdf ticket: {str(e)}")
        pass
    
    try:
        html_content = render_to_string('email_templates/ticket.html', {'event': event, 'user': user, 'booking': booking})

        email_message = EmailMessage(
            subject = f'Thank You for Booking with Promises and Pearls',
            body = html_content,
            from_email = settings.EMAIL_HOST_USER,
            to = [user.email],
        )

        email_message.content_subtype = 'html'
        if pdf_path:
            email_message.attach_file(pdf_path)
        
        email_message.send(fail_silently=False)
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        pass