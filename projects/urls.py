from django.urls        import path
from projects.views     import ProjectDetailView, ProjectListView, ProjectRegisterView

urlpatterns = [
    path('/<int:id>', ProjectDetailView.as_view()),
    path('', ProjectListView.as_view()),
    path('', ProjectRegisterView.as_view())
]
