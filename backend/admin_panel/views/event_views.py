import json

from events.models import Event, EventImage, EventVideo

from users.utils import jwt_decode, auth_admin
from users.models import CustomUser

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from datetime import datetime, timedelta

# ================================================================ #
# ========== Admin Panel Event API's (Protected by JWT) ========== #
# ================================================================ #
    
@csrf_exempt
def create_event(request):
    if request.method == 'POST':
        try:
            bearer = request.headers.get('Authorization')
            if not bearer:
                return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
            
            token = bearer.split()[1]
            if not auth_admin(token):
                return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
            
            decoded_token = jwt_decode(token)
            user_email = decoded_token.get('email')
            
            try:
                user = CustomUser.objects.get(email=user_email)
            except CustomUser.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)
            
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'message': 'Invalid JSON data.'}, status=400)
            
            required_fields = [
                'title',
                'description',
                'event_type',
                'location',
                'start_date',
                'end_date',
                'event_price',
                'max_attendees',
            ]
            
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'success': False, 'message': f'{field.capitalize()} is required.'}, status=400)
            
            try:
                start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%dT%H:%M') + timedelta(hours=3)
                end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%dT%H:%M') + timedelta(hours=3)
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Invalid date format.'}, status=400)
            
            if start_date < datetime.now():
                return JsonResponse({'success': False, 'message': 'Event start date cannot be in the past.'}, status=400)
            
            if end_date < start_date:
                return JsonResponse({'success': False, 'message': 'Event end date cannot be before the start date.'}, status=400)
            
            try:
                event = Event.objects.create(
                    organizer=user,
                    title=data.get('title'),
                    description=data.get('description'),
                    event_type=data.get('event_type'),
                    location=data.get('location'),
                    start_date=start_date,
                    end_date=end_date,
                    event_price=data.get('event_price'),
                    max_attendees=data.get('max_attendees'),
                )
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'Error creating event: {str(e)}'}, status=500)
            
            return JsonResponse({'success': True, 'message': 'Event created successfully.', 'data': {
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
            }}, status=201)
        
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Unexpected error: {str(e)}'}, status=500)
    
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

@csrf_exempt
def get_all_events(request):
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Unexpected error: {str(e)}'}, status=500)
    
    if request.method == 'GET':
        try:
            events = Event.objects.all()
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
def get_event_by_id(request, event_id):
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Unexpected error: {str(e)}'}, status=500)
    
    if request.method == 'GET':
        try:
            event = Event.objects.get(id=event_id)
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

@csrf_exempt
def update_event(request, event_id):
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Unexpected error: {str(e)}'}, status=500)
    
    if request.method == 'PUT' or request.method == 'PATCH':
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Event not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error retrieving event: {str(e)}'}, status=500)
        
        data = json.loads(request.body)
        
        for field, value in data.items():
            if field in ['title', 'description', 'event_type', 'location', 'start_date', 'end_date', 'event_price', 'max_attendees']:
                setattr(event, field, value)
        
        event.save()
        return JsonResponse({'success': True, 'message': 'Event updated successfully.', 'data': {
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

@csrf_exempt
def delete_event(request, event_id):
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Unexpected error: {str(e)}'}, status=500)
    
    if request.method == 'DELETE':
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Event not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error retrieving event: {str(e)}'}, status=500)
        
        event.delete()
        return JsonResponse({'success': True, 'message': 'Event deleted successfully.'}, status=200)
    
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

@csrf_exempt
def get_events_by_organizer(request, user_id):
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Unexpected error: {str(e)}'}, status=500)
    
    if request.method == 'GET':
        try:
            events = Event.objects.filter(organizer__id=user_id)
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