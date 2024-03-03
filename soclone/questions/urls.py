"""URLs for the questions app."""
from django.urls import path

from . import views

app_name = "questions"
urlpatterns = [
    # ex: /questions/
    path("", views.QuestionsView.as_view(), name="questions"),
    path("create/", views.CreateQuestionView.as_view(), name="question_create"),
    path("tags/", views.TagsView.as_view(), name="tags"),
]
