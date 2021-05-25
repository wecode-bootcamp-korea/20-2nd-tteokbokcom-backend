import json
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
