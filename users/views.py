import json
import requests
from json                   import JSONDecodeError

from django.http            import JsonResponse
from django.views           import View
from django.core.exceptions import ValidationError
from django.db.utils        import DataError

from users.models           import User
from users.validators       import (DuplicatedEntryError,
                                    validate_username, 
                                    validate_email, 
                                    validate_password, 
                                    validate_duplicate)
from utils.auth             import (UnauthorizationError,
                                    check_password,
                                    issue_token,
                                    hash_password,
                                    )
from utils.decorators        import login_required
from django.utils.decorators import method_decorator

class SignUpView(View):
    def post(self, request):
        try:
            data            = json.loads(request.body)
            username        = validate_username(data['username'])
            email           = validate_email(data['email'])
            password        = validate_password(data['password'])
            hashed_password = hash_password(password)
            validate_duplicate(User, data)

            user = User.objects.create(
                username = username,
                email    = email,
                password = hashed_password,
            )

            return JsonResponse({"status": "SUCCESS", "data": {"user": user.to_dict('password')}}, status=200)

        except JSONDecodeError as e:
            return JsonResponse({"status": "JSON_DECODE_ERROR", "message": e.msg}, status=400)

        except ValidationError as e:
            return JsonResponse({"status": "INVALID_DATA_ERROR", "message": e.message}, status=400)

        except KeyError as e:
            return JsonResponse({"status": "KEY_ERROR", "message": f'Key Error in Field "{e.args[0]}"'}, status=400)

        except DuplicatedEntryError as e:
            return JsonResponse({"status": "DUPLICATED_ENTRY_ERROR", "message": e.err_message}, status=409)

        except DataError as e:
            return JsonResponse({"status": "INVALID_DATA_ERROR", "message": e.args[1]}, status=400)

class SignInView(View):
    def post(self, request):
        try:
            data     = json.loads(request.body)
            email    = data['email']
            user     = User.objects.get(email = email)

            if user.kakao_id:
                return JsonResponse({"status": "INVALID_SIGNIN_TYPE", "message": "Please Use Social Login Method"}, status=400)

            check_password(data['password'], user)
            token    = issue_token(user)

            return JsonResponse({"status": "SUCCESS", "data": {"token": token}}, status=200)

        except JSONDecodeError as e:
            return JsonResponse({"status": "JSON_DECODE_ERROR", "message": e.msg}, status=400)

        except KeyError as e:
            return JsonResponse({"status": "KEY_ERROR", "message": f'Key Error in Field "{e.args[0]}"'}, status=400)

        except User.DoesNotExist:
            return JsonResponse({"status": "INVALID_USER_ERROR"}, status=401)

        except UnauthorizationError as e:
            return JsonResponse({"status": "UNAUTHORIZATION_ERROR", "message": e.err_message}, status=401)

class KakaoSignInView(View):
    def post(self, request):
        try:
            data         = json.loads(request.body)
            access_token = data['access_token']
            response     = requests.get('https://kapi.kakao.com/v2/user/me', headers={"Authorization": f'Bearer ${access_token}'})
            data         = response.json()

            if response.status_code != 200:
                return JsonResponse({"status": "API_ERROR", "message": data['msg']}, status=response.status_code)

            kakao_id           = data['id']
            username           = data['properties']['nickname']
            profile_image_url  = data['properties']['profile_image']
            email              = data['kakao_account'].get('email')

            if (User.objects.filter(kakao_id = kakao_id).exists()):
                user = User.objects.get(kakao_id = kakao_id)

            else:
                validate_duplicate(User, {"username": username, "email": email, "profile_image_url": profile_image_url})
                user = User.objects.create(
                                            username          = username,
                                            email             = email,
                                            profile_image_url = profile_image_url,
                                            kakao_id          = kakao_id,
                                          )
            token    = issue_token(user)

            return JsonResponse({"status": "SUCCESS", "data": {"token": token}}, status=200)

        except KeyError as e:
            return JsonResponse({"status": "KEY_ERROR", "message": f'Key Error in Field "{e.args[0]}"'}, status=400)

        except requests.exceptions.Timeout as e:
            return JsonResponse({"status": "TIMEOUT_ERROR", "message": e.response.message}, status=e.response.status_code)

        except requests.exceptions.ConnectionError as e:
            return JsonResponse({"status": "CONNECTION_ERROR", "message": e.response.message}, status=e.response.status_code)

        except requests.exceptions.HTTPError as e:
            return JsonResponse({"status": "TIMEOUT_ERROR", "message": e.response.message}, status=e.response.status_code)

        except DuplicatedEntryError as e:
            return JsonResponse({"status": "DUPLICATED_ENTRY_ERROR", "message": e.err_message}, status=409)

class MeView(View):
    @method_decorator(login_required())
    def get(self, request):
        user = request.user
        return JsonResponse({"status": "SUCCESS", "data": {"user": user.to_dict('password')}}, status=200)
