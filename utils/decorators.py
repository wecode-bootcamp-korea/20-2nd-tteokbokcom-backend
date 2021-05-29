import jwt
import functools

from django.http import JsonResponse

from users.models import User
from utils.auth import get_user_from_jwt, decode_jwt

def login_required():
    def decorator(function):
        @functools.wraps(function)
        def wrapper_login_required(request, *args, **kwargs):
            token = request.headers.get('Authorization')
            
            try:

                if token:
                    user         = get_user_from_jwt(token)
                    request.user = user
                    return function(request, *args, **kwargs)
                else:
                    return JsonResponse({"status": "UNAUTHORIZATION_ERROR", "message": "Login Required."}, status=401)
                
            except jwt.exceptions.ExpiredSignatureError as e:
                return JsonResponse({"status": "TOKEN_ERROR", "message": e.args[0]}, status=401)

            except jwt.exceptions.InvalidSignatureError as e:
                return JsonResponse({"status": "TOKEN_ERROR", "message": e.args[0]}, status=401)

            except jwt.exceptions.DecodeError as e:
                return JsonResponse({"status": "TOKEN_ERROR", "message": e.args[0]}, status=401)

            except User.DoesNotExist:
                return JsonResponse({"status": "INVALID_USER"}, status=401)
                
        return wrapper_login_required
    return decorator

def check_user():
    def decorator(function):
        @functools.wraps(function)
        def wrapper_check_user(request, *args, **kwargs):
            try:
                token = request.headers.get('Authorization')
                
                if token:
                    user         = User.objects.get(pk=decode_jwt(token).get('user_id'))
                    request.user = user
                    return function(request, *args, **kwargs)
                else:
                    request.user = None
                    return function(request, *args, **kwargs)
            except:
                request.user = None
                return function(request, *args, **kwargs)

        return wrapper_check_user
    return decorator