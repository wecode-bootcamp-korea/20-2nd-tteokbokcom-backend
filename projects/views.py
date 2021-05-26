import json
from json.decoder                   import JSONDecodeError
from datetime                       import datetime
from decimal                        import Decimal

from django.views                   import View
from django.utils.decorators        import method_decorator
from django.db.models               import Sum, F, Value, When, Case
from django.http.response           import JsonResponse
from django.db.models.functions     import Coalesce
from django.db.models.aggregates    import Count
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
                'funding_amount'       : 0 if project.donation_set.count() == 0 else int(project.donation_set.aggregate(Sum('funding_option__amount'))['funding_option__amount__sum']),
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

class ProjectListView(View):
    @method_decorator(check_user())
    def get(self, request):
        queries       = request.GET
        user          = request.user
        progress_min  = queries.get('progressMin')
        progress_max  = queries.get('progressMax')
        amount_min    = queries.get('amountMin')
        amount_max    = queries.get('amountMax')
        category      = queries.get('category')
        status        = queries.get('status')
        liked         = queries.get('liked')
        sort_criteria = queries.get('sorted', 'default')
        search        = queries.get('search')

        filter_set = {
            'progress__gte'      : progress_min,
            'progress__lte'      : progress_max,
            'funding_amount__gte': amount_min,
            'funding_amount__lte': amount_max,
            'category__name'     : category,
            'status'             : status,
            'is_liked'           : True if liked is not None else False,
        }

        filter_set = { k: v for k, v in filter_set.items() if v }

        sortby_set = {
            'default': '-created_at',
            'latest' : '-created_at',
            'people' : '-funding_count',
            'amount' : '-funding_amount',
            'old'    : 'end_date'
        }

        project_list = Project.objects.all().select_related('category', 'creater')\
                                            .prefetch_related('donation_set', 'likes_set')\
                                            .annotate(funding_amount = Coalesce(Sum('donation__funding_option__amount'), Decimal(0)))\
                                            .annotate(funding_count = Coalesce(Count('donation'), 0))\
                                            .annotate(progress = 100 * F('funding_amount')/F('target_fund'))\
                                            .annotate(status = Case(When(end_date__lt = datetime.now(), then=Value("done")),
                                                                    When(launch_date__gt = datetime.now(), then=Value("scheduled")),
                                                                    default=Value("ing")))\
                                            .annotate(is_liked = Case(When(likes__user = user, then=Value(True)),
                                                                      default=Value(False)))\
                                            .filter(**filter_set)\
                                            .order_by(sortby_set[sort_criteria])

        if search:
            project_list = project_list.filter(title__contains=search) | project_list.filter(summary__contains=search)

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
            'is_liked'       : project.is_liked if user else False,
        } for project in project_list]

        return JsonResponse({'status': "SUCCESS", "data": {'num_projects': len(projects), 'projects': projects} }, status=200)
