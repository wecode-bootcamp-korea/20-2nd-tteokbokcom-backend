import json

from django.test    import TestCase, Client

from users.models   import User
from utils.auth     import get_user_from_jwt, hash_password

class UsersTest(TestCase):
    client = Client()

    def setUp(self):
        User.objects.create(
            username = "테스트유저01",
            email    = "test01@tteokbok.com",
            password = hash_password("password")
        )

    def tearDown(self):
        User.objects.all().delete()

    def case_signupview_post_success(self):
        user_data = {
            "username": "김떡볶",
            "email"   : "ilove@tteokbok.com",
            "password": "tteokbokki"
        }

        response = self.client.post('/users/signup', data=json.dumps(user_data), content_type="application/json")
        user_id  = User.objects.get(email=user_data["email"]).id
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
                "status": "SUCCESS",
                "data"  : {
                    "user": {
                        "id"               : user_id,
                        "username"         : "김떡볶",
                        "introduction"     : None,
                        "email"            : "ilove@tteokbok.com",
                        "profile_image_url": "",
                        "kakao_id"         : None
                    }
                }
            }
        )

    def case_signupview_post_duplicated_email(self):
        user_data = {
            "username": "김떡볶",
            "email"   : "ilove@tteokbok.com",
            "password": "tteokbokki"
        }

        response = self.client.post('/users/signup', data=json.dumps(user_data), content_type="application/json")

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json(), {
            "status" : "DUPLICATED_ENTRY_ERROR",
            "message": "Entry email is duplicated."
            }
        )

    def case_signupview_post_invalid_data(self):
        user_data_invalid_email = {
            "username": "김떡볶",
            "email"   : "iloveteokbok.com",
            "password": "tteokbokki"
        }
        user_data_too_short_password = {
            "username": "김떡볶",
            "email"   : "iloveteokbok.com",
            "password": "123"
        }
        user_data_too_long_password = {
            "username": "김떡볶",
            "email"   : "iloveteokbok.com",
            "password": "12345"*5
        }
        user_data_too_short_username = {
            "username": "김",
            "email"   : "iloveteokbok.com",
            "password": "tteokbokki"
        }
        user_data_too_long_username = {
            "username": "김"*25,
            "email"   : "iloveteokbok.com",
            "password": "tteokbokki"
        }

        response_list = []
        response_list.append(self.client.post('/users/signup', data=json.dumps(user_data_invalid_email), content_type="application/json"))
        response_list.append(self.client.post('/users/signup', data=json.dumps(user_data_too_short_password), content_type="application/json"))
        response_list.append(self.client.post('/users/signup', data=json.dumps(user_data_too_long_password), content_type="application/json"))
        response_list.append(self.client.post('/users/signup', data=json.dumps(user_data_too_short_username), content_type="application/json"))
        response_list.append(self.client.post('/users/signup', data=json.dumps(user_data_too_long_username), content_type="application/json"))

        for response in response_list:
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json()['status'], "INVALID_DATA_ERROR")

    def test_email_signup(self):
        self.case_signupview_post_success()
        self.case_signupview_post_duplicated_email()
        self.case_signupview_post_invalid_data()

    def case_signinview_post_success(self):
        user_data = {
            "email"   : "test01@tteokbok.com",
            "password": "password"
        }

        response = self.client.post('/users/signin', data=user_data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.get(email=user_data["email"]), get_user_from_jwt(response.json()["data"]["token"]))

    def case_signinview_post_user_not_exist(self):
        user_data = {
            "email"   : "user_not_exist@tteokbok.com",
            "password": "password"
        }
        response = self.client.post('/users/signin', data=user_data, content_type="application/json")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["status"], "INVALID_USER_ERROR")

    def case_signinview_post_wrong_password(self):
        user_data = {
            "email"   : "test01@tteokbok.com",
            "password": "wrongpassword"
        }

        response = self.client.post('/users/signin', data=user_data, content_type="application/json")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["status"], "UNAUTHORIZATION_ERROR")

    def test_email_signin(self):
        self.case_signinview_post_success()
        self.case_signinview_post_user_not_exist()
        self.case_signinview_post_wrong_password()
