import json
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings

from events.models import EventRequest, Event

from users.utils import jwt_decode, auth_user
from users.models import CustomUser

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from datetime import datetime, timedelta, timezone

from django.core.mail import EmailMessage

@csrf_exempt
def create_eventrequest(request):
    if request.method == 'POST':
        try:
            bearer = request.headers.get('Authorization')
            if not bearer:
                return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
            
            token = bearer.split()[1]
            if not auth_user(token):
                return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
            
            decoded_token = jwt_decode(token)
            user_email = decoded_token.get('email')
            
            try:
                user = CustomUser.objects.get(email=user_email)
            except CustomUser.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)

            data = json.loads(request.body)
            expected_start_date = datetime.strptime(data.get('expected_start_date'), '%Y-%m-%dT%H:%M')
            expected_end_date = datetime.strptime(data.get('expected_end_date'), '%Y-%m-%dT%H:%M')

            if expected_start_date < datetime.now():
                return JsonResponse({'success': False, 'message': 'Event start date cannot be in the past.'}, status=400)

            if expected_end_date < expected_start_date:
                return JsonResponse({'success': False, 'message': 'Event end date cannot be before the start date.'}, status=400)

            event_request = EventRequest.objects.create(
                user=user,
                title=data.get('title'),
                description=data.get('description'),
                expected_start_date=expected_start_date,
                expected_end_date=expected_end_date,
                location=data.get('location'),
                expected_guests=data.get('expected_guests'),
                budget=data.get('budget'),
            )

            superuser_html = render_to_string('email_templates/superuser_eventrequest.html', {
                'event_request': event_request,
                'user': user,
                'user_email': user_email,
            })

            user_html = render_to_string('email_templates/user_eventrequest.html', {
                'event_request': event_request,
                'user': user,
                'user_email': user_email,
            })

            superuser_email_message = EmailMessage(
                subject='New Event Request Submission',
                body=superuser_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.SUPERUSER_EMAIL],
            )
            superuser_email_message.content_subtype = 'html'
            superuser_email_message.send(fail_silently=False)

            user_email_message = EmailMessage(
                subject='Your Event Request is Received!',
                body=user_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user_email],
            )
            user_email_message.content_subtype = 'html'
            user_email_message.send(fail_silently=False)

            return JsonResponse({'success': True, 'message': 'Event request created successfully', 'data': {
                'id': event_request.id,
                'title': event_request.title,
                'description': event_request.description,
                'expected_start_date': event_request.expected_start_date,
                'expected_end_date': event_request.expected_end_date,
                'location': event_request.location,
                'expected_guests': event_request.expected_guests,
                'budget': event_request.budget,
                'created_at': event_request.created_at,
                'updated_at': event_request.updated_at,
            }}, status=201)
        
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON in request body.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Error requesting event: {str(e)}"}, status=500)

@csrf_exempt
def edit_eventrequest(request, request_id):
    if request.method == 'POST':
        try:
            bearer = request.headers.get('Authorization')
            if not bearer:
                return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
            
            token = bearer.split()[1]
            if not auth_user(token):
                return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
            
            decoded_token = jwt_decode(token)
            user_email = decoded_token.get('email')
            
            try:
                user = CustomUser .objects.get(email=user_email)
            except CustomUser .DoesNotExist:
                return JsonResponse({'success': False, 'message': 'User  not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Error requesting event: {e}"}, status=500)
        
        try:
            event_request = EventRequest.objects.get(id=request_id, user=user)
        except EventRequest.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Event request not found.'}, status=404)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON in request body.'}, status=400)
        
        event_request.title = data.get('title', event_request.title)
        event_request.description = data.get('description', event_request.description)
        event_request.expected_start_date = datetime.strptime(data.get('expected_start_date', event_request.expected_start_date), '%Y-%m-%dT%H:%M') + timedelta(hours=3)
        event_request.expected_end_date = datetime.strptime(data.get('expected_end_date', event_request.expected_end_date), '%Y-%m-%dT%H:%M') + timedelta(hours=3)
        event_request.location = data.get('location', event_request.location)
        event_request.expected_guests = data.get('expected_guests', event_request.expected_guests)
        event_request.budget = data.get('budget', event_request.budget)
        
        if event_request.expected_start_date < datetime.now() + timedelta(hours=3):
            return JsonResponse({'success': False, 'message': 'Event start date cannot be in the past.'}, status=400)

        if event_request.expected_end_date < event_request.expected_start_date:
            return JsonResponse({'success': False, 'message': 'Event end date cannot be before the start date.'}, status=400)
        
        event_request.save()
        
        return JsonResponse({'success': True, 'message': 'Event request updated successfully', 'data': {
            'id': event_request.id,
            'title': event_request.title,
            'description': event_request.description,
            'expected_start_date': event_request.expected_start_date,
            'expected_end_date': event_request.expected_end_date,
            'location': event_request.location,
            'expected_guests': event_request.expected_guests,
            'budget': event_request.budget,
            'created_at': event_request.created_at,
            'updated_at': event_request.updated_at,
        }}, status=200)

@csrf_exempt
def delete_eventrequest(request, request_id):
    if request.method == 'POST':
        try:
            bearer = request.headers.get('Authorization')
            if not bearer:
                return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
            
            token = bearer.split()[1]
            if not auth_user(token):
                return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
            
            decoded_token = jwt_decode(token)
            user_email = decoded_token.get('email')
            
            try:
                user = CustomUser .objects.get(email=user_email)
            except CustomUser .DoesNotExist:
                return JsonResponse({'success': False, 'message': 'User  not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Error requesting event: {e}"}, status=500)
        
        try:
            event_request = EventRequest.objects.get(id=request_id, user=user)
            event_request.delete()
            return JsonResponse({'success': True, 'message': 'Event request deleted successfully', 'data': {}}, status=204)
        except EventRequest.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Event request not found.'}, status=404)

@csrf_exempt
def get_eventrequests_by_user(request):
    if request.method == 'GET':
        try:
            bearer = request.headers.get('Authorization')
            if not bearer:
                return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
            
            token = bearer.split()[1]
            if not auth_user(token):
                return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
            
            decoded_token = jwt_decode(token)
            user_email = decoded_token.get('email')
            
            try:
                user = CustomUser .objects.get(email=user_email)
            except CustomUser .DoesNotExist:
                return JsonResponse({'success': False, 'message': 'User  not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f"Error requesting event: {e}"}, status=500)
        
        event_requests = EventRequest.objects.filter(user=user)
        return JsonResponse({'success': True, 'message': 'Event requests fetched successfully', 'data': [{
            'id': event_request.id,
            'title': event_request.title,
            'description': event_request.description,
            'expected_start_date': event_request.expected_start_date,
            'expected_end_date': event_request.expected_end_date,
            'location': event_request.location,
            'expected_guests': event_request.expected_guests,
            'budget': event_request.budget,
            'created_at': event_request.created_at,
            'updated_at': event_request.updated_at,
        } for event_request in event_requests]})