import json
from json.decoder            import JSONDecodeError

from django.views            import View
from django.db.models        import Sum
from django.db               import transaction
from django.http.response    import JsonResponse
from django.conf             import settings
from django.utils.decorators import method_decorator

from .models                 import Category, Project, Tag, FundingOption
from utils.s3_file_util      import S3FileUtils
from utils.decorators        import login_required

class ProjectRegisterView(View):
    DEFAULT_AMOUNT      = 1000
    DEFAULT_DESCRIPTION = '선물을 선택하지 않고 밀어만 줍니다'
    DEFAULT_TITLE       = '기본 선물'

    @method_decorator(login_required())
    def get(self, request):
        user_info = {
            'creater'           : request.user.username,
            'profile_img'       : request.user.profile_image_url,
            'introduction'      : request.user.introduction
        }

        return JsonResponse({'user_info': user_info})

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