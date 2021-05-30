from django.urls       import path

from projects.views    import ProjectRegisterView

urlpatterns = [
    path('', ProjectRegisterView.as_view()),
]
