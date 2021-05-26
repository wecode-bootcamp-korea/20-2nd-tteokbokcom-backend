from django.test     import TestCase, Client

from users.models    import User
from projects.models import Project, Category, FundingOption, Donation
from utils.auth      import hash_password

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

        User.objects.create(
            username          = '테스트유저',
            introduction      = '테스트 유저 소개',
            email             = 'test@tteokbok.com',
            password          = hash_password("password"),
            profile_image_url = 'profile_image.jpeg'
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

        Project.objects.create(
            title           = '프로젝트2',
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
            project     = Project.objects.get(id=2),
            title       = '기본옵션',
            description = '선물을 선택하지 않고 밀어만 줍니다.'
        )

        FundingOption.objects.create(
            amount      = 2000,
            project     = Project.objects.get(id=2),
            title       = '옵션1',
            description = '옵션1에 대한 설명',
            remains     = 50
        )

        FundingOption.objects.create(
            amount      = 3000,
            project     = Project.objects.get(id=2),
            title       = '옵션2',
            description = '옵션2에 대한 설명',
            remains     = 40
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

    def test_project_detail_funding_amount_zero(self):
        client   = Client()
        response = client.get('/projects/2')
        self.assertEqual(response.json(),
            {
                "result" : {
                    "id" : 2,
                    "title_image_url"      : "title_image.jpg",
                    "title"                : "프로젝트2",
                    "category"             : "카테고리1",
                    "creater"              : "유저1",
                    "creater_profile_image": "profile1.jpg",
                    "creater_introduction" : "유저소개",
                    "summary"              : "프로젝트 설명",
                    "funding_amount"       : 0,
                    "target_amount"        : 1000000,
                    "total_sponsor"        : 0,
                    "end_date"             : "2021-05-31T00:00:00",
                    "funding_option"       :
                    [
                        {
                        "option_id"        : 4,
                        "amount"           : 1000,
                        "title"            : "기본옵션",
                        "remains"          : None,
                        "description"      : "선물을 선택하지 않고 밀어만 줍니다.",
                        "selected_funding" : 0
                        },
                        {
                        "option_id"        : 5,
                        "amount"           : 2000,
                        "title"            : "옵션1",
                        "remains"          : 50,
                        "description"      : "옵션1에 대한 설명",
                        "selected_funding" : 0
                        },
                        {
                        "option_id"        : 6,
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

    def test_project_detail_patch_like_success(self):
        client    = Client()
        user_data = {
            "email"   : "test@tteokbok.com",
            "password": "password"
        }
        project        = Project.objects.get(title="프로젝트1")
        login_response = client.post('/users/signin', data=user_data, content_type="application/json")
        token          = login_response.json().get("data").get("token")

        is_liked_before     = client.get(f'/projects/{project.id}', HTTP_AUTHORIZATION=token, content_type="application/json").json().get('result').get('is_liked')
        like_patch_response = client.patch(f'/projects/{project.id}', HTTP_AUTHORIZATION=token, content_type="application/json")
        is_liked_after      = client.get(f'/projects/{project.id}', HTTP_AUTHORIZATION=token, content_type="application/json").json().get('result').get('is_liked')

        self.assertEqual(like_patch_response.status_code, 200)
        self.assertEqual(like_patch_response.json(), {"status": "SUCCESS", 'message': 'is_liked changed to True'})
        self.assertEqual(is_liked_before, not is_liked_after)

    def test_project_detail_patch_like_unauthorized(self):
        client  = Client()
        project = Project.objects.get(title="프로젝트1")

        like_patch_response = client.patch(f'/projects/{project.id}', content_type="application/json")
        self.assertEqual(like_patch_response.status_code, 401)
        self.assertEqual(like_patch_response.json(), {'status': 'UNAUTHORIZATION_ERROR', 'message': 'Login Required.'})

class ProjectListTest(TestCase):
    def setUp(self):
        user_1 = User.objects.create(
                    username          = 'testuser1',
                    email             = 'test1@mail.com',
                    password          = hash_password('12345678'),
                    profile_image_url = "test.jpg"
                )

        user_2 = User.objects.create(
                    username          = 'testuser2',
                    email             = 'test2@mail.com',
                    password          = hash_password('12345678'),
                    profile_image_url = "test.jpg"
                )

        category_1 = Category.objects.create(
                        name = '카테고리1'
                    )

        category_2 = Category.objects.create(
                        name = '카테고리2'
                    )

        self.project_1 = Project.objects.create(
                        title           = '타이틀1',
                        creater         = user_1,
                        summary         = '프로젝트 설명',
                        category        = category_1,
                        title_image_url = 'test.jpg',
                        target_fund     = 100000,
                        launch_date     = '2021-05-20',
                        end_date        = '2021-05-29'
                    )

        self.project_2 = Project.objects.create(
                        title           = '타이틀2',
                        creater         = user_1,
                        summary         = '프로젝트 설명',
                        category        = category_2,
                        title_image_url = 'test.jpg',
                        target_fund     = 300000,
                        launch_date     = '2021-05-24',
                        end_date        = '2121-05-30'
                    )

        self.project_3 = Project.objects.create(
                        title           = '타이틀2',
                        creater         = user_2,
                        summary         = '프로젝트 설명 테스트',
                        category        = category_2,
                        title_image_url = 'test.jpg',
                        target_fund     = 500000,
                        launch_date     = '2121-05-24',
                        end_date        = '2121-05-30'
                    )

        fund_1 = FundingOption.objects.create(
                    amount = 1000,
                    project = self.project_1,
                    remains = 10,
                    title = '상품옵션1',
                    description = '상품설명'
                )

        fund_2 = FundingOption.objects.create(
                    amount = 2000,
                    project = self.project_1,
                    remains = 10,
                    title = '상품옵션2',
                    description = '상품설명'
                )

        fund_3 = FundingOption.objects.create(
                    amount = 3000,
                    project = self.project_1,
                    remains = 10,
                    title = '상품옵션3',
                    description = '상품설명'
                )

        fund_4 = FundingOption.objects.create(
                    amount = 1000,
                    project = self.project_2,
                    remains = 10,
                    title = '상품옵션1',
                    description = '상품설명'
                )

        fund_5 = FundingOption.objects.create(
                    amount = 2000,
                    project = self.project_2,
                    remains = 10,
                    title = '상품옵션2',
                    description = '상품설명'
                )

        fund_6 = FundingOption.objects.create(
                    amount = 3000,
                    project = self.project_2,
                    remains = 10,
                    title = '상품옵션3',
                    description = '상품설명'
                )

        donation_1 = Donation.objects.create(
                        funding_option = fund_1,
                        project = self.project_1,
                        user = user_1
                    )

        donation_2 = Donation.objects.create(
                        funding_option = fund_2,
                        project = self.project_1,
                        user = user_1
                    )

        donation_3 = Donation.objects.create(
                        funding_option = fund_5,
                        project = self.project_2,
                        user = user_2
                    )

        donation_4 = Donation.objects.create(
                        funding_option = fund_6,
                        project = self.project_2,
                        user = user_2
                    )

    def tearDown(self):
        Donation.objects.all().delete()
        FundingOption.objects.all().delete()
        Project.objects.all().delete()
        User.objects.all().delete()
        Category.objects.all().delete()

    def test_projectlistview_get_success(self):
        client = Client()
        response = client.get('/projects')
        self.assertEqual(response.json(),
            {
                "status":"SUCCESS",
                "data":{
                    "num_projects":3,
                    "projects":[
                        {
                            "id":self.project_3.id,
                            "title_image_url":"test.jpg",
                            "title":"타이틀2",
                            "category":"카테고리2",
                            "creater":"testuser2",
                            "summary":"프로젝트 설명 테스트",
                            "funding_amount":0.0,
                            "funding_count":0,
                            "target_amount":500000.0,
                            "launch_date":"2121-05-24T00:00:00",
                            "end_date":"2121-05-30T00:00:00",
                            "status":"scheduled",
                            "progress":"0.000000"
                        },
                        {
                            "id":self.project_2.id,
                            "title_image_url":"test.jpg",
                            "title":"타이틀2",
                            "category":"카테고리2",
                            "creater":"testuser1",
                            "summary":"프로젝트 설명",
                            "funding_amount":5000.0,
                            "funding_count":2,
                            "target_amount":300000.0,
                            "launch_date":"2021-05-24T00:00:00",
                            "end_date":"2121-05-30T00:00:00",
                            "status":"ing",
                            "progress":"1.666667"
                        },
                        {
                            "id": self.project_1.id,
                            "title_image_url":"test.jpg",
                            "title":"타이틀1",
                            "category":"카테고리1",
                            "creater":"testuser1",
                            "summary":"프로젝트 설명",
                            "funding_amount":3000.0,
                            "funding_count":2,
                            "target_amount":100000.0,
                            "launch_date":"2021-05-20T00:00:00",
                            "end_date":"2021-05-29T00:00:00",
                            "status":"done",
                            "progress":"3.000000"
                        }
                    ]
                }
            })
    def test_projectlistview_get_sort_amount(self):
        client = Client()
        response = client.get('/projects?sorted=amount')
        self.assertEqual(response.json(),
            {
                "status":"SUCCESS",
                "data":{
                    "num_projects":3,
                    "projects":[
                        {
                            "id":self.project_2.id,
                            "title_image_url":"test.jpg",
                            "title":"타이틀2",
                            "category":"카테고리2",
                            "creater":"testuser1",
                            "summary":"프로젝트 설명",
                            "funding_amount":5000.0,
                            "funding_count":2,
                            "target_amount":300000.0,
                            "launch_date":"2021-05-24T00:00:00",
                            "end_date":"2121-05-30T00:00:00",
                            "status":"ing",
                            "progress":"1.666667"
                        },
                        {
                            "id": self.project_1.id,
                            "title_image_url":"test.jpg",
                            "title":"타이틀1",
                            "category":"카테고리1",
                            "creater":"testuser1",
                            "summary":"프로젝트 설명",
                            "funding_amount":3000.0,
                            "funding_count":2,
                            "target_amount":100000.0,
                            "launch_date":"2021-05-20T00:00:00",
                            "end_date":"2021-05-29T00:00:00",
                            "status":"done",
                            "progress":"3.000000"
                        },
                        {
                            "id":self.project_3.id,
                            "title_image_url":"test.jpg",
                            "title":"타이틀2",
                            "category":"카테고리2",
                            "creater":"testuser2",
                            "summary":"프로젝트 설명 테스트",
                            "funding_amount":0.0,
                            "funding_count":0,
                            "target_amount":500000.0,
                            "launch_date":"2121-05-24T00:00:00",
                            "end_date":"2121-05-30T00:00:00",
                            "status":"scheduled",
                            "progress":"0.000000"
                        },
                    ]
                }
            })
    def test_projectlistview_get_sort_people(self):
        client = Client()
        response = client.get('/projects?sorted=people')
        self.assertEqual(response.json(),
            {
                "status":"SUCCESS",
                "data":{
                    "num_projects":3,
                    "projects":[
                        {
                            "id":self.project_2.id,
                            "title_image_url":"test.jpg",
                            "title":"타이틀2",
                            "category":"카테고리2",
                            "creater":"testuser1",
                            "summary":"프로젝트 설명",
                            "funding_amount":5000.0,
                            "funding_count":2,
                            "target_amount":300000.0,
                            "launch_date":"2021-05-24T00:00:00",
                            "end_date":"2121-05-30T00:00:00",
                            "status":"ing",
                            "progress":"1.666667"
                        },
                        {
                            "id": self.project_1.id,
                            "title_image_url":"test.jpg",
                            "title":"타이틀1",
                            "category":"카테고리1",
                            "creater":"testuser1",
                            "summary":"프로젝트 설명",
                            "funding_amount":3000.0,
                            "funding_count":2,
                            "target_amount":100000.0,
                            "launch_date":"2021-05-20T00:00:00",
                            "end_date":"2021-05-29T00:00:00",
                            "status":"done",
                            "progress":"3.000000"
                        },
                        {
                            "id":self.project_3.id,
                            "title_image_url":"test.jpg",
                            "title":"타이틀2",
                            "category":"카테고리2",
                            "creater":"testuser2",
                            "summary":"프로젝트 설명 테스트",
                            "funding_amount":0.0,
                            "funding_count":0,
                            "target_amount":500000.0,
                            "launch_date":"2121-05-24T00:00:00",
                            "end_date":"2121-05-30T00:00:00",
                            "status":"scheduled",
                            "progress":"0.000000"
                        },
                    ]
                }
            })
    def test_projectlistview_get_sort_old(self):
        client = Client()
        response = client.get('/projects?sorted=old')
        self.assertEqual(response.json(),
            {
                "status":"SUCCESS",
                "data":{
                    "num_projects":3,
                    "projects":[
                        {
                            "id": self.project_1.id,
                            "title_image_url":"test.jpg",
                            "title":"타이틀1",
                            "category":"카테고리1",
                            "creater":"testuser1",
                            "summary":"프로젝트 설명",
                            "funding_amount":3000.0,
                            "funding_count":2,
                            "target_amount":100000.0,
                            "launch_date":"2021-05-20T00:00:00",
                            "end_date":"2021-05-29T00:00:00",
                            "status":"done",
                            "progress":"3.000000"
                        },
                        {
                            "id":self.project_2.id,
                            "title_image_url":"test.jpg",
                            "title":"타이틀2",
                            "category":"카테고리2",
                            "creater":"testuser1",
                            "summary":"프로젝트 설명",
                            "funding_amount":5000.0,
                            "funding_count":2,
                            "target_amount":300000.0,
                            "launch_date":"2021-05-24T00:00:00",
                            "end_date":"2121-05-30T00:00:00",
                            "status":"ing",
                            "progress":"1.666667"
                        },
                        {
                            "id":self.project_3.id,
                            "title_image_url":"test.jpg",
                            "title":"타이틀2",
                            "category":"카테고리2",
                            "creater":"testuser2",
                            "summary":"프로젝트 설명 테스트",
                            "funding_amount":0.0,
                            "funding_count":0,
                            "target_amount":500000.0,
                            "launch_date":"2121-05-24T00:00:00",
                            "end_date":"2121-05-30T00:00:00",
                            "status":"scheduled",
                            "progress":"0.000000"
                        }
                    ]
                }
            })

    def test_projectlistview_get_search(self):
        client = Client()
        response = client.get('/projects?search=테스트')
        self.assertEqual(response.json(),
            {
                "status":"SUCCESS",
                "data":{
                    "num_projects":1,
                    "projects":[
                        {
                            "id":self.project_3.id,
                            "title_image_url":"test.jpg",
                            "title":"타이틀2",
                            "category":"카테고리2",
                            "creater":"testuser2",
                            "summary":"프로젝트 설명 테스트",
                            "funding_amount":0.0,
                            "funding_count":0,
                            "target_amount":500000.0,
                            "launch_date":"2121-05-24T00:00:00",
                            "end_date":"2121-05-30T00:00:00",
                            "status":"scheduled",
                            "progress":"0.000000"
                        }
                    ]
                }
            })

    def test_projectlistview_get_status_done(self):
        client = Client()
        response = client.get('/projects?status=done')
        self.assertEqual(response.json(),
            {
                "status":"SUCCESS",
                "data":{
                    "num_projects":1,
                    "projects":[
                        {
                            "id": self.project_1.id,
                            "title_image_url":"test.jpg",
                            "title":"타이틀1",
                            "category":"카테고리1",
                            "creater":"testuser1",
                            "summary":"프로젝트 설명",
                            "funding_amount":3000.0,
                            "funding_count":2,
                            "target_amount":100000.0,
                            "launch_date":"2021-05-20T00:00:00",
                            "end_date":"2021-05-29T00:00:00",
                            "status":"done",
                            "progress":"3.000000"
                        }
                    ]
                }
            })

    def test_projectlistview_get_status_ing(self):
        client = Client()
        response = client.get('/projects?status=ing')
        self.assertEqual(response.json(),
            {
                "status":"SUCCESS",
                "data":{
                    "num_projects":1,
                    "projects":[
                        {
                            "id":self.project_2.id,
                            "title_image_url":"test.jpg",
                            "title":"타이틀2",
                            "category":"카테고리2",
                            "creater":"testuser1",
                            "summary":"프로젝트 설명",
                            "funding_amount":5000.0,
                            "funding_count":2,
                            "target_amount":300000.0,
                            "launch_date":"2021-05-24T00:00:00",
                            "end_date":"2121-05-30T00:00:00",
                            "status":"ing",
                            "progress":"1.666667"
                        }
                    ]
                }
            })

    def test_projectlistview_get_status_(self):
        client = Client()
        response = client.get('/projects?status=scheduled')
        self.assertEqual(response.json(),
            {
                "status":"SUCCESS",
                "data":{
                    "num_projects":1,
                    "projects":[
                        {
                            "id":self.project_3.id,
                            "title_image_url":"test.jpg",
                            "title":"타이틀2",
                            "category":"카테고리2",
                            "creater":"testuser2",
                            "summary":"프로젝트 설명 테스트",
                            "funding_amount":0.0,
                            "funding_count":0,
                            "target_amount":500000.0,
                            "launch_date":"2121-05-24T00:00:00",
                            "end_date":"2121-05-30T00:00:00",
                            "status":"scheduled",
                            "progress":"0.000000"
                        }
                    ]
                }
            })

    def test_projectlistview_get_filter_progress(self):
        client = Client()
        response = client.get('/projects?progressMin=1&progressMax=2')
        self.assertEqual(response.json(),
            {
                "status":"SUCCESS",
                "data":{
                    "num_projects":1,
                    "projects":[
                        {
                            "id":self.project_2.id,
                            "title_image_url":"test.jpg",
                            "title":"타이틀2",
                            "category":"카테고리2",
                            "creater":"testuser1",
                            "summary":"프로젝트 설명",
                            "funding_amount":5000.0,
                            "funding_count":2,
                            "target_amount":300000.0,
                            "launch_date":"2021-05-24T00:00:00",
                            "end_date":"2121-05-30T00:00:00",
                            "status":"ing",
                            "progress":"1.666667"
                        }
                    ]
                }
            })

    def test_projectlistview_get_filter_amount(self):
        client = Client()
        response = client.get('/projects?amountMin=4000&amountMax=6000')
        self.assertEqual(response.json(),
            {
                "status":"SUCCESS",
                "data":{
                    "num_projects":1,
                    "projects":[
                        {
                            "id":self.project_2.id,
                            "title_image_url":"test.jpg",
                            "title":"타이틀2",
                            "category":"카테고리2",
                            "creater":"testuser1",
                            "summary":"프로젝트 설명",
                            "funding_amount":5000.0,
                            "funding_count":2,
                            "target_amount":300000.0,
                            "launch_date":"2021-05-24T00:00:00",
                            "end_date":"2121-05-30T00:00:00",
                            "status":"ing",
                            "progress":"1.666667"
                        }
                    ]
                }
            })

    def test_projectlistview_get_filter_category(self):
        client = Client()
        response = client.get('/projects?category=카테고리2')
        self.assertEqual(response.json(),
            {
                "status":"SUCCESS",
                "data":{
                    "num_projects":2,
                    "projects":[
                        {
                            "id":self.project_3.id,
                            "title_image_url":"test.jpg",
                            "title":"타이틀2",
                            "category":"카테고리2",
                            "creater":"testuser2",
                            "summary":"프로젝트 설명 테스트",
                            "funding_amount":0.0,
                            "funding_count":0,
                            "target_amount":500000.0,
                            "launch_date":"2121-05-24T00:00:00",
                            "end_date":"2121-05-30T00:00:00",
                            "status":"scheduled",
                            "progress":"0.000000"
                        },
                        {
                            "id":self.project_2.id,
                            "title_image_url":"test.jpg",
                            "title":"타이틀2",
                            "category":"카테고리2",
                            "creater":"testuser1",
                            "summary":"프로젝트 설명",
                            "funding_amount":5000.0,
                            "funding_count":2,
                            "target_amount":300000.0,
                            "launch_date":"2021-05-24T00:00:00",
                            "end_date":"2121-05-30T00:00:00",
                            "status":"ing",
                            "progress":"1.666667"
                        }
                    ]
                }
            })
