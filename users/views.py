from django.http                import JsonResponse
from django.views               import View
from django.utils.decorators    import method_decorator

from utils.decorators        import login_required

class MeView(View):
    @method_decorator(login_required())
    def get(self, request):
        user = request.user
        return JsonResponse({"status": "SUCCESS", "data": {"user": user.to_dict('password')}}, status=200)
