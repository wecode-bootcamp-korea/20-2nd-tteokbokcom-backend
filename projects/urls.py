from django.urls    import path
from projects.views import ProjectDetailView, ProjectListView

urlpatterns = [
    path('', ProjectDetailView.as_view()),
    path('/<int:id>', ProjectDetailView.as_view()),
    path('', ProjectListView.as_view()),
]