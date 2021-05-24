import json
import requests
from json                   import JSONDecodeError

from django.http            import JsonResponse
from django.views           import View

from users.models           import User
from utils.auth             import (UnauthorizationError,
                                    check_password,
                                    issue_token,
                                    )

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
            data               = json.loads(request.body)
            access_token       = data['access_token']
            user_info_response = requests.get('https://kapi.kakao.com/v2/user/me', headers={"Authorization": f'Bearer ${access_token}'})
            user_info          = user_info_response.json()
            kakao_id           = user_info['id']
            username           = user_info['properties']['nickname']
            profile_image_url  = user_info['properties']['profile_image']
            email              = user_info['kakao_account'].get('email')

            if (User.objects.filter(kakao_id = kakao_id).exists()):
                user = User.objects.get(kakao_id = kakao_id)

            else:
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
