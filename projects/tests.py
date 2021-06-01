from unittest.mock  import patch

from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile

from users.models    import User
from projects.models import Project, Category, FundingOption
from utils.auth     import hash_password, issue_token

class ProjectPaymentTest(TestCase):
    client = Client()

    @classmethod
    def setUpClass(cls):
        User.objects.create(
            username          = '유저1',
            introduction      = '유저소개',
            email             = 'test1@mail.com',
            password          = hash_password('12345678')
        )

        Category.objects.create(name='카테고리1')

        Project.objects.create(
            title           = '프로젝트1',
            creater         = User.objects.get(id=1),
            summary         = '프로젝트 설명',
            category        = Category.objects.get(id=1),
            title_image_url = 'title_image.jpg',
            target_fund     = 1000000,
            launch_date     = '2021-05-01',
            end_date        = '2021-05-31',
            created_at      = '2021-05-01'
        )

        FundingOption.objects.create(
            amount      = 1000,
            project     = Project.objects.get(id=1),
            title       = '기본옵션',
            description = '선물을 선택하지 않고 밀어만 줍니다.'
        )

        FundingOption.objects.create(
            amount      = 2000,
            project     = Project.objects.get(id=1),
            title       = '옵션1',
            description = '옵션1에 대한 설명',
            remains     = 50
        )

        FundingOption.objects.create(
            amount      = 3000,
            project     = Project.objects.get(id=1),
            title       = '옵션2',
            description = '옵션2에 대한 설명',
            remains     = 40
        )

    @classmethod
    def tearDownClass(cls):
        FundingOption.objects.all().delete()
        Project.objects.all().delete()
        User.objects.all().delete()
        Category.objects.all().delete()

    def test_project_payment_success(self):
        user_data = {
            'email'   : 'test1@mail.com',
            'password': '12345678'
        }

        data = {
            'id': 1,
            'option_id': 1
        }

        signin_response = self.client.post('/users/signin', data=user_data, content_type="application/json")
        token    = signin_response.json().get("data").get("token")
        response = self.client.put("/projects", HTTP_AUTHORIZATION=token, data=data, content_type="application/json")
        print(response)
