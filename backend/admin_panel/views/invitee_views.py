import json

from events.models import Event, Invitee

from users.utils import jwt_decode, auth_admin
from users.models import CustomUser

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def add_invitees_to_event(request, event_id):
    if request.method != 'POST':
        return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return JsonResponse({"success": False, "message": "Event not found."}, status=404)

    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Unexpected error: {str(e)}'}, status=500)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data.'}, status=400)

    if not isinstance(data, list):
        return JsonResponse({'success': False, 'message': 'Request body must contain a list of invitees.'}, status=400)
    
    invitees = []

    for invitee_data in data:
        required_fields = [
            'email',
            'name',
        ]

        for field in required_fields:
            if field not in invitee_data:
                return JsonResponse({'success': False, 'message': f'{field.capitalize()} is required.'}, status=400)

        invitee = Invitee(event=event, email=invitee_data.get('email'), name=invitee_data.get('name', ''))
        invitee.save()
        invitees.append({
            "id": invitee.id,
            "email": invitee.email,
            "name": invitee.name,
            "invite_status": invitee.invite_status,
            "created_at": invitee.created_at,
            "updated_at": invitee.updated_at,
        })

    return JsonResponse({"success": True, "message": "Invitees added successfully.", "data": invitees}, status=201)


@csrf_exempt
def get_invitees_for_event(request, event_id):
    if request.method != 'GET':
        return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return JsonResponse({"success": False, "message": "Event not found."}, status=404)

    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Unexpected error: {str(e)}'}, status=500)

    invitees = event.invitees.all()
    invitees_data = []
    for invitee in invitees:
        invitees_data.append({
            'id': invitee.id,
            'email': invitee.email,
            'name': invitee.name,
            'invite_status': invitee.invite_status,
            'created_at': invitee.created_at,
            'updated_at': invitee.updated_at
        })

    return JsonResponse({"success": True, "message": "Invitees retrieved successfully.", "data": invitees_data}, status=200)


@csrf_exempt
def update_invitee_status(request, event_id, invitee_id):
    if request.method != 'PATCH':
        return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return JsonResponse({"success": False, "message": "Event not found."}, status=404)

    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Unexpected error: {str(e)}'}, status=500)

    try:
        invitee = Invitee.objects.get(id=invitee_id, event=event)
    except Invitee.DoesNotExist:
        return JsonResponse({"success": False, "message": "Invitee not found."}, status=404)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data.'}, status=400)

    invitee.invite_status = data.get('invite_status', invitee.invite_status)
    invitee.save()

    return JsonResponse({"success": True, "message": "Invitee status updated successfully."}, status=200)


@csrf_exempt
def remove_invitee_from_event(request, event_id, invitee_id):
    if request.method != 'DELETE':
        return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return JsonResponse({"success": False, "message": "Event not found."}, status=404)

    try:
        bearer = request.headers.get('Authorization')
        if not bearer:
            return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
        
        token = bearer.split()[1]
        if not auth_admin(token):
            return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Unexpected error: {str(e)}'}, status=500)

    try:
        invitee = Invitee.objects.get(id=invitee_id, event=event)
    except Invitee.DoesNotExist:
        return JsonResponse({"success": False, "message": "Invitee not found."}, status=404)

    invitee.delete()

    return JsonResponse({"success": True, "message": "Invitee removed successfully."}, status=200)