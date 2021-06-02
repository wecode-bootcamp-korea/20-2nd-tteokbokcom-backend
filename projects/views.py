import json
from datetime                       import datetime
from decimal                        import Decimal

from django.views                   import View
from django.conf                    import settings
from django.db                      import transaction
from django.db.models               import Sum, F, Value, When, Case
from django.db.models.functions     import Coalesce
from django.db.models.aggregates    import Count
from django.http.response           import JsonResponse
from django.utils.decorators        import method_decorator

from projects.models                import Category, Project, Tag, FundingOption
from utils.s3_file_util             import S3FileUtils
from utils.decorators               import login_required

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

class ProjectRegisterView(View):
    DEFAULT_AMOUNT      = 1000
    DEFAULT_DESCRIPTION = '선물을 선택하지 않고 밀어만 줍니다'
    DEFAULT_TITLE       = '기본 선물'

    # @method_decorator(login_required())
    # def get(self, request):
    #     user_info = {
    #         'creater'           : request.user.username,
    #         'profile_img'       : request.user.profile_image_url,
    #         'introduction'      : request.user.introduction
    #     }

    #     return JsonResponse({'user_info': user_info})

    @method_decorator(login_required())
    def post(self, request):
        data                      = json.loads(request.POST['info'], strict=False)
        title                     = data['title']
        summary                   = data['summary']
        category_name             = data['category']
        target_fund               = data['target_fund']
        tags_name                 = data.get('tags')
        launch_date               = data['launch_date']
        end_date                  = data['end_date']
        reward_one                = data['reward_one']
        reward_two                = data['reward_two']
        profile_image             = request.FILES['profile_img']
        request.user.username     = data['username']
        request.user.introduction = data['introduction']
        project_image             = request.FILES['project_img']

        for file_content_type in (profile_image.content_type, project_image.content_type):
            if not ('image' in file_content_type):
                return JsonResponse({'message': 'INVALID_FILE_TYPE'}, status=400)

        resized_images = S3FileUtils.resize_image(project_image=project_image, profile_image=profile_image)

        with transaction.atomic():
            filename = S3FileUtils.generate_filename(project_image=project_image, profile_image=profile_image)

            project = Project.objects.create(
                title                = title,
                creater              = request.user,
                summary              = summary,
                category             = Category.objects.get(name=category_name),
                title_image_url      = settings.AWS_S3_FILE_URL % (request.user.id ,filename['project_image']),
                target_fund          = target_fund,
                launch_date          = launch_date,
                end_date             = end_date
            )

            FundingOption.objects.create(
                amount      = self.DEFAULT_AMOUNT,
                project     = project,
                title       = self.DEFAULT_TITLE,
                description = self.DEFAULT_DESCRIPTION
            )

            for funding_option in [reward_one, reward_two]:
                FundingOption.objects.create(
                    amount      = funding_option['amount'],
                    project     = project,
                    remains     = funding_option['remains'],
                    title       = funding_option['title'],
                    description = funding_option['description']
                )

            tags = [Tag.objects.get_or_create(name = tag_name)[0] for tag_name in tags_name]
            for tag in tags:
                tag.project_set.add(project)

            if request.user.profile_image_url is not None and profile_image is not None:
                S3FileUtils.file_delete(request.user.id, request.user.profile_image_url)

            request.user.profile_image_url = settings.AWS_S3_FILE_URL % (request.user.id ,filename['profile_image'])
            request.user.save()

            S3FileUtils.file_upload(request.user.id, filename=filename, **resized_images)

        return JsonResponse({'messages': 'SUCCESS'}, status=200)
