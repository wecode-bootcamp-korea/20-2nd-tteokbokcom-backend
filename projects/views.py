import json
from json.decoder                   import JSONDecodeError

from django.views                   import View
from django.db.models               import Sum
from django.http.response           import JsonResponse
from django.utils.decorators        import method_decorator

from projects.models                import Category, Project, Tag, FundingOption
from users.models                   import Likes
from utils.decorators               import login_required, check_user

class ProjectDetailView(View):
    @method_decorator(check_user())
    def get(self, request, id):
        try:
            project = Project.objects.prefetch_related('fundingoption_set', 'fundingoption_set__donation_set').get(id=id)
            user    = request.user

            result = {
                'id'                   : project.id,
                "is_liked"             : False if not user else Likes.objects.filter(user=user, project=project).exists(),
                'title_image_url'      : project.title_image_url,
                'title'                : project.title,
                'category'             : project.category.name,
                'creater'              : project.creater.username,
                'creater_profile_image': project.creater.profile_image_url,
                'creater_introduction' : project.creater.introduction,
                'summary'              : project.summary,
                'funding_amount'       : int(project.donation_set.aggregate(Sum('funding_option__amount'))['funding_option__amount__sum']),
                'target_amount'        : int(project.target_fund),
                'total_sponsor'        : project.donation_set.count(),
                'end_date'             : project.end_date,
                "funding_option"       :
                [{
                    'option_id'        : int(funding_option.id),
                    "amount"           : int(funding_option.amount),
                    "title"            : funding_option.title,
                    "remains"          : None if funding_option.remains is None else int(funding_option.remains),
                    "description"      : funding_option.description,
                    "selected_funding" : int(funding_option.donation_set.count())
                } for funding_option in project.fundingoption_set.all()],
            }

            return JsonResponse({'result': result}, status=200)

        except Project.DoesNotExist:
            return JsonResponse({'messages': 'DOES_NOT_EXIST'}, status=404)

    @method_decorator(login_required())
    def patch(self, request, id):
        try:
            user = request.user
            project = Project.objects.get(id=id)
            is_liked = Likes.objects.filter(user=user, project=project).exists()
            
            if is_liked:
                Likes.objects.filter(user=user, project=project).delete()
            else:
                Likes.objects.create(user = user, project = project)

            return JsonResponse({"status": "SUCCESS", 'message': f'is_liked changed to {not is_liked}'}, status=200)

        except Project.DoesNotExist:
            return JsonResponse({"status": "INVALID_PROJECT_ERROR", 'messages': 'Project does not exist.'}, status=404)
