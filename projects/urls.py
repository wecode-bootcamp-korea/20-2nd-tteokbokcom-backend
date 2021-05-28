from projects.models import Project
from django.urls import path

from .views import ProjectDetailView

urlpatterns = [
    path('/<int:id>', ProjectDetailView.as_view()),
]
