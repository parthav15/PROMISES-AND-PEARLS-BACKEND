import json

from users.utils import jwt_encode, jwt_decode, auth_admin
from users.models import CustomUser

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate

@csrf_exempt
def admin_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data.'}, status=400)
        
        if not email or not password:
            return JsonResponse({'success': False, 'message': 'Email and password are required.'}, status=400)

        user = authenticate(request, username=email, password=password)
        
        if user is None:
            return JsonResponse({'success': False, 'message': 'Invalid email or password.'}, status=401)

        if not user.is_admin:
            return JsonResponse({'success': False, 'message': 'User is not an admin.'}, status=403)

        token = jwt_encode(user.email)
        return JsonResponse({'success': True, 'message': 'Admin logged in successfully.', 'token': token}, status=200)
    
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)