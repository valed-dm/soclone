"""URLs for the questions app."""
from django.urls import path

from . import views

app_name = "questions"
urlpatterns = [
    # ex: /questions/
    path("", views.QuestionsView.as_view(), name="questions"),
    path("<int:pk>/", views.QuestionFullView.as_view(), name="question"),
    path("create/", views.QuestionCreateView.as_view(), name="question_create"),
    path("tags/", views.TagsView.as_view(), name="tags"),
    path(
        "a_rating/<int:q_pk>/<int:a_pk>/<int:useful>",
        views.rating,
        name="a_rating",
    ),
    path("q_rating/<int:q_pk>/<int:useful>", views.rating, name="q_rating"),
]
