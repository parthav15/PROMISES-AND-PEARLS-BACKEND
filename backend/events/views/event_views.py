import json

from events.models import EventRequest, Event

from users.utils import jwt_decode, auth_user
from users.models import CustomUser

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from datetime import datetime, timedelta

@csrf_exempt
def get_public_events(request):
    if request.method == 'GET':
        try:
            events = Event.objects.filter(event_type=Event.PUBLIC)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error retrieving events: {str(e)}'}, status=500)
        
        return JsonResponse({'success': True, 'message': 'Events retrieved successfully.', 'data': [{
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'event_type': event.event_type,
            'location': event.location,
            'start_date': event.start_date,
            'end_date': event.end_date,
            'event_price': event.event_price,
            'max_attendees': event.max_attendees,
            'organizer': {
                'id': event.organizer.id,
                'email': event.organizer.email,
                'first_name': event.organizer.first_name,
                'last_name': event.organizer.last_name,
                'phone_number': event.organizer.phone_number,
                'profile_picture': event.organizer.profile_picture.url,
            },
            'images': [{
                'id': image.id,
                'url': image.image.url,
            } for image in event.event_images.all()],
            'videos': [{
                'id': video.id,
                'url': video.video.url,
            } for video in event.event_videos.all()],
        } for event in events]}, status=200)
    
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)
    
@csrf_exempt
def get_specific_public_event(request):
    if request.method == 'GET':
        try:
            event_id = request.GET.get('event_id')
            if not event_id:
                return JsonResponse({'success': False, 'message': 'Event ID is required.'}, status=400)
            
            event = Event.objects.get(id=event_id, event_type=Event.PUBLIC)
        except Event.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Event not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error retrieving event: {str(e)}'}, status=500)
        
        return JsonResponse({'success': True, 'message': 'Event retrieved successfully.', 'data': {
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'event_type': event.event_type,
            'location': event.location,
            'start_date': event.start_date,
            'end_date': event.end_date,
            'event_price': event.event_price,
            'max_attendees': event.max_attendees,
            'organizer': {
                'id': event.organizer.id,
                'email': event.organizer.email,
                'first_name': event.organizer.first_name,
                'last_name': event.organizer.last_name,
                'phone_number': event.organizer.phone_number,
                'profile_picture': event.organizer.profile_picture.url,
            },
            'images': [{
                'id': image.id,
                'url': image.image.url,
            } for image in event.event_images.all()],
            'videos': [{
                'id': video.id,
                'url': video.video.url,
            } for video in event.event_videos.all()],
        }}, status=200)
    
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)
