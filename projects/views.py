from datetime                   import datetime
from decimal                    import Decimal

from django.views               import View
from django.db.models           import Sum, F, Value, When, Case
from django.http.response       import JsonResponse
from django.db.models.functions import Coalesce
from django.db.models.aggregates import Count

from projects.models            import Project

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
        queries = request.GET
        progress_min  = queries.get('progressMin')
        progress_max  = queries.get('progressMax')
        amount_min    = queries.get('amountMin')
        amount_max    = queries.get('amountMax')
        category      = queries.get('category')
        status        = queries.get('status')
        sort_criteria = queries.get('sorted', 'default')
        search        = queries.get('search')

        filter_set = {
            'progress__gte'      : progress_min,
            'progress__lte'      : progress_max,
            'funding_amount__gte': amount_min,
            'funding_amount__lte': amount_max,
            'category__name'     : category,
            'status'             : status
        }

        filter_set = { k: v for k, v in filter_set.items() if v }

        sortby_set = {
            'default': '-created_at',
            'latest' : '-created_at',
            'people' : '-funding_count',
            'amount' : '-funding_amount',
            'old'    : 'end_date'
        }

        project_list = Project.objects.all().order_by('-id')\
                                            .select_related('category', 'creater')\
                                            .prefetch_related('donation_set')\
                                            .annotate(funding_amount = Coalesce(Sum('donation__funding_option__amount'), Decimal(0)))\
                                            .annotate(funding_count = Coalesce(Count('donation'), 0))\
                                            .annotate(progress = 100 * F('funding_amount')/F('target_fund'))\
                                            .annotate(status = Case(When(end_date__lt = datetime.now(), then=Value("done")),
                                                                    When(launch_date__gt = datetime.now(), then=Value("scheduled")),
                                                                    default=Value("ing")))

        project_list = project_list.filter(**filter_set).order_by(sortby_set[sort_criteria])

        if search:
            project_list = project_list.filter(title__contains = search) | project_list.filter(summary__contains = search)

        projects = [{
            'id'             : project.id,
            'title_image_url': project.title_image_url,
            'title'          : project.title,
            'category'       : project.category.name,
            'creater'        : project.creater.username,
            'summary'        : project.summary,
            'funding_amount' : float(project.funding_amount),
            'funding_count'  : project.funding_count,
            'target_amount'  : float(project.target_fund),
            'launch_date'    : project.launch_date,
            'end_date'       : project.end_date,
            'status'         : project.status,
            'progress'       : project.progress,
        } for project in project_list]

        return JsonResponse({'status': "SUCCESS", "data": {'num_projects': len(projects), 'projects': projects} }, status=200)
