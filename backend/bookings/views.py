from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings

from bookings.models import Booking, Ticket
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
                lead_user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)
            except KeyError:
                return JsonResponse({'success': False, 'message': 'Invalid token format.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Unexpected error: {str(e)}'}, status=500)
        
        data = json.loads(request.body)

        event_id = data.get('event_id')
        ticket_quantity = data.get('ticket_quantity', 1)
        user_details = data.get('user_details')

        event = Event.objects.get(id=event_id)

        booking = Booking.objects.create(
            event=event,
            lead_user=lead_user,
            user_details=user_details,
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
                'lead_user': booking.lead_user.email,
                'user_details': booking.user_details,
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
    
@csrf_exempt
@require_http_methods(["GET"])
def get_booking_detail(request):
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_user(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
        
        try:
            email = jwt_decode(token)['email']
            lead_user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)
        except KeyError:
            return JsonResponse({'success': False, 'message': 'Invalid token format.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Unexpected error: {str(e)}'}, status=500)
    
    try:
        booking_id = request.GET.get('booking_id')
        booking = Booking.objects.get(id=booking_id, lead_user=lead_user)
    except Booking.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Booking not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({
        'success': True,
        'message': 'Booking details retrieved successfully',
        'data': {
            'id': booking.id,
            'event': {
                'id': booking.event.id,
                'title': booking.event.title,
                'location': booking.event.location,
                'start_date': booking.event.start_date.strftime("%B %d, %Y, %I:%M %p") if booking.event.start_date else None,
                'end_date': booking.event.end_date.strftime("%B %d, %Y, %I:%M %p") if booking.event.end_date else None,
            },
            'lead_user': {
                'id': booking.lead_user.id,
                'email': booking.lead_user.email,
                'first_name': booking.lead_user.first_name,
                'last_name': booking.lead_user.last_name
            },
            'ticket_quantity': booking.ticket_quantity,
            'total_price': str(booking.total_price),
            'booking_status': booking.booking_status
        }
    })

def send_ticket(event, booking):
    try:
        for attendee in booking.user_details:
            try:
                ticket = Ticket.objects.create(
                    booking=booking,
                    attendee=attendee
                )
                ticket.generate_qr_code()
                ticket.save()

                pdf_path = generate_pdf_ticket(event, booking, ticket)
                
                html_content = render_to_string('email_templates/ticket.html', {
                    'event': event,
                    'booking': booking,
                    'ticket': ticket
                })

                email_message = EmailMessage(
                    subject=f'Your Ticket for {event.title}',
                    body=html_content,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[ticket.attendee['email']],
                )
                email_message.content_subtype = 'html'
                
                if pdf_path:
                    email_message.attach_file(pdf_path)
                
                email_message.send(fail_silently=False)
                
            except Exception as e:
                print(f"Error processing ticket for {attendee['email']}: {str(e)}")
        
    except Exception as e:
        print(f"Error in send_ticket: {str(e)}")

@csrf_exempt
@require_http_methods(["POST"])
def send_ticket_api(request):
    try:
        data = request.POST
        event_id = data.get('event_id')
        booking_id = data.get('booking_id')

        event = Event.objects.get(id=event_id)
        booking = Booking.objects.get(id=booking_id)

        send_ticket(event, booking)

        return JsonResponse({
            'success': True,
            'message': 'Ticket sent successfully',
        })
    
    except Event.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Event not found',
        }, status=404)
    
    except Booking.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Booking not found',
        }, status=404)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Unexpected error: {str(e)}',
        }, status=500)
