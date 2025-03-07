import json

from events.models import Event, EventImage, EventVideo

from users.utils import jwt_decode, auth_admin

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def upload_event_images(request):
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Unexpected error: {str(e)}'}, status=500)
    
    if request.method == 'POST':
        try:
            event_id = request.POST.get('event_id')
            if not event_id:
                return JsonResponse({'success': False, 'message': 'Event ID is required.'}, status=400)
            
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Event not found.'}, status=404)
        
        images = request.FILES.getlist('images')
        if not images:
            return JsonResponse({'success': False, 'message': 'Images are required.'}, status=400)
        
        for image in images:
            EventImage.objects.create(
                event=event,
                image=image
            )
        return JsonResponse({'success': True, 'message': 'Images uploaded successfully.'}, status=201)
    
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

@csrf_exempt
def get_all_images_for_event(request):
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Unexpected error: {str(e)}'}, status=500)
    
    if request.method == 'POST':
        try:
            event_id = request.POST.get('event_id')
            if not event_id:
                return JsonResponse({'success': False, 'message': 'Event ID is required.'}, status=400)
            
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Event not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error retrieving event: {str(e)}'}, status=500)
        
        images = EventImage.objects.filter(event=event)
        return JsonResponse({'success': True, 'message': 'Images retrieved successfully.', 'data': [{
            'id': image.id,
            'image': image.image.url,
        } for image in images]}, status=200)
    
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

@csrf_exempt
def delete_event_image(request):
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Unexpected error: {str(e)}'}, status=500)
    
    if request.method == 'POST':
        try:
            event_id = request.POST.get('event_id')
            image_id = request.POST.get('image_id')
            if not event_id or not image_id:
                return JsonResponse({'success': False, 'message': 'Event ID and Image ID are required.'}, status=400)
            
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Event not found.'}, status=404)
        
        try:
            image = EventImage.objects.get(id=image_id, event=event)
        except EventImage.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Image not found.'}, status=404)
        
        image.delete()
        return JsonResponse({'success': True, 'message': 'Image deleted successfully.'}, status=200)
    
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

@csrf_exempt
def upload_event_video(request):
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Unexpected error: {str(e)}'}, status=500)
    
    if request.method == 'POST':
        try:
            event_id = request.POST.get('event_id')
            if not event_id:
                return JsonResponse({'success': False, 'message': 'Event ID is required.'}, status=400)
            
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Event not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error retrieving event: {str(e)}'}, status=500)
        
        videos = request.FILES.getlist('videos')
        if not videos:
            return JsonResponse({'success': False, 'message': 'Videos are required.'}, status=400)
        
        for video in videos:
            EventVideo.objects.create(
                event=event,
                video=video
            )
        return JsonResponse({'success': True, 'message': 'Videos uploaded successfully.'}, status=201)
    
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

@csrf_exempt
def get_all_videos_for_event(request):
    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Unexpected error: {str(e)}'}, status=500)
    
    if request.method == 'POST':
        try:
            event_id = request.POST.get('event_id')
            if not event_id:
                return JsonResponse({'success': False, 'message': 'Event ID is required.'}, status=400)
            
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Event not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error retrieving event: {str(e)}'}, status=500)
        
        videos = EventVideo.objects.filter(event=event)
        return JsonResponse({'success': True, 'message': 'Videos retrieved successfully.', 'data': [{
            'id': video.id,
            'video': video.video.url,
        } for video in videos]}, status=200)
    
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)
