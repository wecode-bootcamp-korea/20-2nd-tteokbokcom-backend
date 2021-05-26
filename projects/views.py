import json
from json.decoder         import JSONDecodeError

from django.views         import View
from django.db.models     import Sum
from django.http.response import JsonResponse

from projects.models              import Project, Donation

class ProjectDetailView(View):
    def get(self, request, id):
        try:
            project = Project.objects.prefetch_related('fundingoption_set', 'fundingoption_set__donation_set').get(id=id)
        
            result = {
                'id'                   : project.id,
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

class ProjectListView(View):

    def get(self, request):
        project_list = Project.objects.all().order_by('-id').select_related('category', 'creater').prefetch_related('donation_set')

        projects = [{
            'id'                   : project.id,
            'title_image_url'      : project.title_image_url,
            'title'                : project.title,
            'category'             : project.category.name,
            'creater'              : project.creater.username,
            'summary'              : project.summary,
            'funding_amount'       : int(project.donation_set.all().aggregate(Sum('funding_option__amount'))['funding_option__amount__sum']),
            'target_amount'        : int(project.target_fund),
            'end_date'             : project.end_date
        } for project in project_list]

        return JsonResponse({'projects': projects}, status=200)
