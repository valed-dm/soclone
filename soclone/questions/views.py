"""Views for the questions app."""
from django.utils import timezone
from django.views import generic

from soclone.questions.models import Question
from soclone.questions.models import Tag


class QuestionsView(generic.ListView):
    """Renders questions table."""

    template_name = "questions/questions.html"
    context_object_name = "questions_list"

    def get_queryset(self):
        """Return the last 10 published questions."""

        return (
            Question.objects.prefetch_related("tags")
            .filter(pub_date__lte=timezone.now())
            .order_by("-pub_date")[:10]
        )


class TagsView(generic.ListView):
    """Renders tags table."""

    template_name = "questions/tags.html"
    context_object_name = "tags_list"

    def get_queryset(self):
        """Return the last 10 published tags."""

        return Tag.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[
            :10
        ]
