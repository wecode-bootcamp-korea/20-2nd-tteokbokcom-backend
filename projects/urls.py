from django.urls import path
from .views      import ProjectDetailView

urlpatterns = [
    path('', ProjectDetailView.as_view()),
]