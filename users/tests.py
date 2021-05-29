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
