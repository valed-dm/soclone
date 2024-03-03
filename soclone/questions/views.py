"""Views for the questions app."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.db.models import F
from django.db.models import OuterRef
from django.db.models import Subquery
from django.db.models.query import QuerySet
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic

from soclone.questions.forms import QuestionForm
from soclone.questions.models import Question
from soclone.questions.models import QuestionView
from soclone.questions.models import QuestionVote
from soclone.questions.models import Tag


class QuestionsView(generic.ListView):
    """Renders questions table."""

    template_name: str = "questions/questions.html"
    context_object_name: str = "questions_list"

    def get_queryset(self) -> QuerySet[Question]:
        """Return the last 10 published questions."""

        latest_questions: QuerySet[Question] = (
            Question.objects.prefetch_related("tags")
            .select_related("user")
            .annotate(
                answers=Count("answer"),
                likes=Subquery(
                    QuestionVote.objects.values("is_useful")
                    .filter(question=OuterRef("id"), is_useful=True)
                    .annotate(qty=Count("question"))
                    .values("qty")
                ),
                dislikes=Subquery(
                    QuestionVote.objects.values("is_useful")
                    .filter(question=OuterRef("id"), is_useful=False)
                    .annotate(qty=Count("question"))
                    .values("qty")
                ),
                views=Subquery(
                    QuestionView.objects.values("question")
                    .filter(question=OuterRef("id"))
                    .annotate(qty=Count("question"))
                    .values("qty")
                ),
                asked=(timezone.now() - F("created_at")),
            )
            .filter(created_at__lte=timezone.now())
            .order_by("-created_at")[:10]
        )

        return latest_questions


class TagsView(generic.ListView):
    """Renders tags table."""

    template_name: str = "questions/tags.html"
    context_object_name: str = "tags_list"

    def get_queryset(self) -> QuerySet[Tag]:
        """Return the last 10 published tags."""

        return Tag.objects.filter(created_at__lte=timezone.now()).order_by(
            "-created_at"
        )[:10]


class CreateQuestionView(LoginRequiredMixin, generic.CreateView):
    """Creates a question."""

    # CreateView class uses the question_form.html template from the templates/questions
    # with the following naming convention: model_form.html
    model = Question
    form_class = QuestionForm
    success_url = reverse_lazy("questions:questions")

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "The question was created successfully.")
        return super().form_valid(form)
