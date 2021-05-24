from django.urls import path
from users.views import MeView, SignInView, KakaoSignInView

urlpatterns = [
    path('/me', MeView.as_view()),
    path('/signup', SignUpView.as_view()),
    path('/signin', SignInView.as_view()),
    path('/signin/kakao', KakaoSignInView.as_view()),
]
