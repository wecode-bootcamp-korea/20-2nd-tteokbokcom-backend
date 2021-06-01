import json
from json.decoder            import JSONDecodeError

from django.views            import View
from django.db.models        import Sum
from django.http.response    import JsonResponse
from django.db               import transaction
from django.utils.decorators import method_decorator

from utils.decorators        import login_required
from .models                 import FundingOption, Project, Donation

class ProjectDetailView(View):
    @method_decorator(login_required())
    def put(self, request):
        try:
            data           = json.loads(request.body)
            project_id     = data['id']
            option_id      = data['option_id']
            project        = Project.objects.get(id=project_id)
            funding_option = FundingOption.objects.get(id=option_id)

            if funding_option.remains == 0:
                return JsonResponse({'messages': 'NO_STOCK'}, status=400)

            with transaction.atomic():
                Donation.objects.create(
                    user                = request.user,
                    project             = project,
                    funding_option      = funding_option
                )

                if funding_option.remains is not None:
                    funding_option.remains -= 1
                    funding_option.save()

            return JsonResponse({'messages': "SUCCESS"}, status=201)
        except KeyError:
            return JsonResponse({'messages': "KEY_ERROR"}, status=400)
        except Project.DoesNotExist:
            return JsonResponse({'messages': "PROJECT_ID_DOES_NOT EXIST"}, status=400)
        except FundingOption.DoesNotExist:
            return JsonResponse({'messages': "FUNDING_OPTION_ID_DOES_NOT EXIST"}, status=400)