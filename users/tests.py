import json
from unittest.mock  import patch

from django.test    import TestCase, Client

from users.models   import User
from utils.auth     import hash_password, issue_token

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

    def test_meview_get_success(self):
        user            = User.objects.get(email="test01@tteokbok.com")
        signin_response = self.client.post("/users/signin", data={"email": user.email, "password": "password"}, content_type="application/json")
        token           = signin_response.json().get("data").get("token")
        response        = self.client.get("/users/me", HTTP_AUTHORIZATION=token, content_type="application/json")

        self.assertEqual(response.json(), {"status": "SUCCESS", "data": {"user": user.to_dict("password")}})

    def test_meview_get_unauthorized(self):
        response = self.client.get("/users/me", content_type="application/json")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"status": "UNAUTHORIZATION_ERROR", "message": "Login Required."})
        
    def test_signinview_post_success(self):
        user_data = {
            "email"   : "test01@tteokbok.com",
            "password": "password"
        }

        response = self.client.post('/users/signin', data=user_data, content_type="application/json")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 
                         {'data': 
                            {'token': issue_token(User.objects.get(email=user_data["email"]))},
                          'status': 'SUCCESS'}
                        )

    def test_signinview_post_user_not_exist(self):
        user_data = {
            "email"   : "user_not_exist@tteokbok.com",
            "password": "password"
        }
        response = self.client.post('/users/signin', data=user_data, content_type="application/json")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"status": "INVALID_USER_ERROR"})

    def test_signinview_post_wrong_password(self):
        user_data = {
            "email"   : "test01@tteokbok.com",
            "password": "wrongpassword"
        }

        response = self.client.post('/users/signin', data=user_data, content_type="application/json")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"status": "UNAUTHORIZATION_ERROR", "message": "Wrong Password Entered."})

    @patch('users.views.requests.get')
    def test_kakaosigninview_post_signup_success(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 12341234,
            "connected_at": "2021-05-26T07:34:57Z",
            "properties": {
                "nickname": "임떡볶",
                "profile_image": "http://k.kakaocdn.net/dn/c9oFJD/btqHR6L8rkC/0Ylcx7xgNvyuPTt7mFKl0K/img_640x640.jpg",
                "thumbnail_image": "http://k.kakaocdn.net/dn/c9oFJD/btqHR6L8rkC/0Ylcx7xgNvyuPTt7mFKl0K/img_110x110.jpg"
            },
            "kakao_account": {
                "profile_needs_agreement": False,
                "profile": {
                    "nickname": "임떡볶",
                    "thumbnail_image_url": "http://k.kakaocdn.net/dn/c9oFJD/btqHR6L8rkC/0Ylcx7xgNvyuPTt7mFKl0K/img_110x110.jpg",
                    "profile_image_url": "http://k.kakaocdn.net/dn/c9oFJD/btqHR6L8rkC/0Ylcx7xgNvyuPTt7mFKl0K/img_640x640.jpg",
                    "is_default_image": False
                },
                "has_email": True,
                "email_needs_agreement": False,
                "is_email_valid": True,
                "is_email_verified": True,
                "email": "tteokbok@kakao.com"
            }
        }

        response = self.client.post('/users/signin/kakao',
                                    data={"access_token": "gxfEZ3VPKWxSrNDV_tO16YnduKfljNC25mz6n2TRUdLNfMQ4JssGHSxDfrQfqTe08wpT8QopcBMAAAF5qFYFMQ"},
                                    content_type="application/json")
        expected_user = User.objects.get(kakao_id=mock_response.json()["id"])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 
                        {'data': 
                            {'token': issue_token(expected_user)},
                         'status': 'SUCCESS'}
                        )

    @patch('users.views.requests.get')
    def test_kakaosigninview_post_signin_success(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 12341234,
            "connected_at": "2021-05-26T07:34:57Z",
            "properties": {
                "nickname": "임떡볶",
                "profile_image": "http://k.kakaocdn.net/dn/c9oFJD/btqHR6L8rkC/0Ylcx7xgNvyuPTt7mFKl0K/img_640x640.jpg",
                "thumbnail_image": "http://k.kakaocdn.net/dn/c9oFJD/btqHR6L8rkC/0Ylcx7xgNvyuPTt7mFKl0K/img_110x110.jpg"
            },
            "kakao_account": {
                "profile_needs_agreement": False,
                "profile": {
                    "nickname": "임떡볶",
                    "thumbnail_image_url": "http://k.kakaocdn.net/dn/c9oFJD/btqHR6L8rkC/0Ylcx7xgNvyuPTt7mFKl0K/img_110x110.jpg",
                    "profile_image_url": "http://k.kakaocdn.net/dn/c9oFJD/btqHR6L8rkC/0Ylcx7xgNvyuPTt7mFKl0K/img_640x640.jpg",
                    "is_default_image": False
                },
                "has_email": True,
                "email_needs_agreement": False,
                "is_email_valid": True,
                "is_email_verified": True,
                "email": "tteokbok@kakao.com"
            }
        }

        response = self.client.post('/users/signin/kakao',
                                    data={"access_token": "gxfEZ3VPKWxSrNDV_tO16YnduKfljNC25mz6n2TRUdLNfMQ4JssGHSxDfrQfqTe08wpT8QopcBMAAAF5qFYFMQ"},
                                    content_type="application/json")
        expected_user = User.objects.get(kakao_id=mock_response.json()["id"])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 
                         {"status": "SUCCESS", 
                          "data"  : 
                            {
                             "token": issue_token(expected_user)
                            }
                         })

    @patch('users.views.requests.get')
    def test_kakaosigninview_post_api_failure(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "code": -401,
            "msg": "this access token is already expired"
        }

        response = self.client.post('/users/signin/kakao',
                                    data={"access_token": "gxfEZ3VPKWxSrNDV_tO16YnduKfljNC25mz6n2TRUdLNfMQ4JssGHSxDfrQfqTe08wpT8QopcBMAAAF5qFYFMQ"},
                                    content_type="application/json")
        
        self.assertEqual(response.status_code, mock_response.status_code)
        self.assertEqual(response.json(), {'message': 'this access token is already expired', 'status': 'API_ERROR'})
    def test_signupview_post_success(self):
        user_data = {
            "username": "김떡볶",
            "email"   : "ilove@tteokbok.com",
            "password": "tteokbokki"
        }

        response = self.client.post('/users/signup', data=user_data, content_type="application/json")
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

    def test_signupview_post_duplicated_email(self):
        user_data = {
            "username": "김떡볶",
            "email"   : "test01@tteokbok.com",
            "password": "tteokbokki"
        }

        response = self.client.post('/users/signup', data=user_data, content_type="application/json")

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json(), {
            "status" : "DUPLICATED_ENTRY_ERROR",
            "message": "Entry email is duplicated."
            }
        )

    def test_signupview_post_invalid_email(self):
        user_data_invalid_email = {
            "username": "김떡볶",
            "email"   : "iloveteokbok.com",
            "password": "tteokbokki"
        }
        response_invalid_email = self.client.post('/users/signup', data=user_data_invalid_email, content_type="application/json")

        self.assertEqual(response_invalid_email.json(), {'message': f'{user_data_invalid_email["email"]} is not an valid email.',
                                                         'status': 'INVALID_DATA_ERROR'})

    def test_signupview_post_too_short_password(self):
        user_data_too_short_password = {
            "username": "김떡볶",
            "email"   : "ilove@teokbok.com",
            "password": "123"
        }
        response_too_short_password = self.client.post('/users/signup', data=user_data_too_short_password, content_type="application/json")

        self.assertEqual(response_too_short_password.json(), {'message': 'Invalid Password Length, Use password length between 6 and 20',
                                                              'status': 'INVALID_DATA_ERROR'})

    def test_signupview_post_too_long_password(self):
        user_data_too_long_password = {
            "username": "김떡볶",
            "email"   : "ilove@teokbok.com",
            "password": "12345"*5
        }
        response_too_long_password  = self.client.post('/users/signup', data=user_data_too_long_password, content_type="application/json")

        self.assertEqual(response_too_long_password.json(), {'message': 'Invalid Password Length, Use password length between 6 and 20',
                                                             'status': 'INVALID_DATA_ERROR'})

    def test_signupview_post_too_short_username(self):
        user_data_too_short_username = {
            "username": "김",
            "email"   : "ilove@teokbok.com",
            "password": "tteokbokki"
        }
        response_short_username     = self.client.post('/users/signup', data=user_data_too_short_username, content_type="application/json")

        self.assertEqual(response_short_username.json(), {'message': 'Invalid Username, Use Username length between 2 and 40',
                                                          'status': 'INVALID_DATA_ERROR'})

    def test_signupview_post_too_long_username(self):
        user_data_too_long_username = {
            "username": "김"*50,
            "email"   : "ilove@teokbok.com",
            "password": "tteokbokki"
        }
        response_too_long_username  = self.client.post('/users/signup', data=user_data_too_long_username, content_type="application/json")

        self.assertEqual(response_too_long_username.json(), {'message': 'Invalid Username, Use Username length between 2 and 40',
                                                             'status': 'INVALID_DATA_ERROR'})
