from django.urls    import path
from projects.views import ProjectDetailView, ProjectView

urlpatterns = [
    path('/<int:id>', ProjectDetailView.as_view()),
    path('', ProjectView.as_view()),
]