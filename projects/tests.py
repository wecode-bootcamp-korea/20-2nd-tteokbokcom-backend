from django.test     import TestCase, Client

from users.models    import User
from projects.models import Project, Category, FundingOption, Donation

class ProjectDetailTest(TestCase):
    @classmethod
    def setUpClass(cls):
        User.objects.create(
            username          = '유저1',
            introduction      = '유저소개',
            email             = 'test1@mail.com',
            password          = '12345678',
            profile_image_url = 'profile1.jpg'
        )

        User.objects.create(
            username          = '유저2',
            introduction      = '유저소개',
            email             = 'test2@mail.com',
            password          = '12345678',
            profile_image_url = 'profile2.jpg'
        )

        User.objects.create(
            username          = '유저3',
            introduction      = '유저소개',
            email             = 'test3@mail.com',
            password          = '12345678',
            profile_image_url = 'profile3.jpg'
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

        Donation.objects.create(
            user           = User.objects.get(id=2),
            project        = Project.objects.get(id=1),
            funding_option = FundingOption.objects.get(id=1),
            created_at     = '2021-05-01',
            updated_at     = '2021-05-01'
        )

        Donation.objects.create(
            user           = User.objects.get(id=3),
            project        = Project.objects.get(id=1),
            funding_option = FundingOption.objects.get(id=1),
            created_at     = '2021-05-01',
            updated_at     = '2021-05-01'
        )

        Donation.objects.create(
            user           = User.objects.get(id=2),
            project        = Project.objects.get(id=1),
            funding_option = FundingOption.objects.get(id=2),
            created_at     = '2021-05-01',
            updated_at     = '2021-05-01'
        )

    @classmethod
    def tearDownClass(cls):
        Donation.objects.all().delete()
        FundingOption.objects.all().delete()
        Project.objects.all().delete()
        User.objects.all().delete()
        Category.objects.all().delete()

    def test_project_detail_success(self):
        client   = Client()
        response = client.get('/projects/1')
        self.assertEqual(response.json(),
            {
                "result" : {
                    "id" : 1,
                    "title_image_url"      : "title_image.jpg",
                    "title"                : "프로젝트1",
                    "category"             : "카테고리1",
                    "creater"              : "유저1",
                    "creater_profile_image": "profile1.jpg",
                    "creater_introduction" : "유저소개",
                    "summary"              : "프로젝트 설명",
                    "funding_amount"       : 4000,
                    "target_amount"        : 1000000,
                    "total_sponsor"        : 3,
                    "end_date"             : "2021-05-31T00:00:00",
                    "funding_option"       :
                    [
                        {
                        "option_id"        : 1,
                        "amount"           : 1000,
                        "title"            : "기본옵션",
                        "remains"          : None,
                        "description"      : "선물을 선택하지 않고 밀어만 줍니다.",
                        "selected_funding" : 2
                        },
                        {
                        "option_id"        : 2,
                        "amount"           : 2000,
                        "title"            : "옵션1",
                        "remains"          : 50,
                        "description"      : "옵션1에 대한 설명",
                        "selected_funding" : 1
                        },
                        {
                        "option_id"        : 3,
                        "amount"           : 3000,
                        "title"            : "옵션2",
                        "remains"          : 40,
                        "description"      : "옵션2에 대한 설명",
                        "selected_funding" : 0
                        },
                    ],
                }
            }
        )
        self.assertEqual(response.status_code, 200)

    def test_project_detail_does_not_exists(self):
        client   = Client()
        response = client.get('/projects/999')
        self.assertEqual(response.json(),
            {
                'messages': 'DOES_NOT_EXIST'
            }
        )
        self.assertEqual(response.status_code, 404)