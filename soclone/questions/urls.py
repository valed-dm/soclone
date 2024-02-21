"""URLs for the questions app."""
from django.urls import path

from . import views

app_name = "questions"
urlpatterns = [
    # ex: /questions/
    path("", views.QuestionsView.as_view(), name="questions"),
    path("tags/", views.TagsView.as_view(), name="tags"),
]
