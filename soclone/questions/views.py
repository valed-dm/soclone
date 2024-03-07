"""Views for the questions app."""
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case
from django.db.models import Count
from django.db.models import F
from django.db.models import OuterRef
from django.db.models import Subquery
from django.db.models import When
from django.db.models.query import QuerySet
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views import generic
from django.views.generic.detail import SingleObjectMixin

from soclone.questions.forms import AnswerForm
from soclone.questions.forms import QuestionForm
from soclone.questions.models import Answer
from soclone.questions.models import Question
from soclone.questions.models import QuestionUniqueViewsStatistics
from soclone.questions.models import QuestionVote
from soclone.questions.models import Tag


class QuestionsView(generic.ListView):
    """Renders questions table."""

    template_name: str = "questions/question_list.html"
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
                    QuestionUniqueViewsStatistics.objects.values("question")
                    .filter(question=OuterRef("id"))
                    .annotate(qty=Count("question"))
                    .values("qty")
                ),
                posed=(timezone.now() - F("created_at")),
            )
            .filter(created_at__lte=timezone.now())
            .order_by("-created_at")[:10]
        )

        return latest_questions


class QuestionDetailView(generic.DetailView):
    """Renders question data."""

    model = Question
    context_object_name = "question"

    def get_context_data(self, **kwargs):
        """Enrich context data with statistics and answer form."""
        context = super().get_context_data(**kwargs)
        q = context["question"]
        cat = q.created_at
        uat = q.updated_at
        views: int = QuestionUniqueViewsStatistics.objects.filter(question=q.id).count()
        answers: QuerySet = (
            Answer.objects.filter(question=q.id).select_related("user").all()
        )
        rating: dict = QuestionVote.objects.aggregate(
            difference=(
                Count(Case(When(is_useful=True, then=1)))
                - Count(Case(When(is_useful=False, then=1)))
            )
        )

        context["posed"] = timezone.now() - cat
        context["modified"] = (
            (timezone.now() - uat) if (uat - cat) > timedelta(seconds=1) else None
        )
        context["views"] = views
        context["rating"] = rating["difference"]
        context["answers_qty"] = answers.count() if answers else 0
        context["answers"] = answers
        context["answer_form"] = AnswerForm
        return context


class QuestionAnswerFormView(SingleObjectMixin, LoginRequiredMixin, generic.FormView):
    """Renders answer form for question."""

    template_name = "questions/question_detail.html"
    form_class = AnswerForm
    model = Answer

    def post(self, request, *args, **kwargs):
        """Enable post request for question."""
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        answer = Answer(
            user=self.request.user,
            question=Question.objects.get(id=self.kwargs.get("pk")),
            body=self.request.POST["body"],
        )
        answer.save()
        messages.success(self.request, "The answer was added successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("questions:question", kwargs={"pk": self.kwargs.get("pk")})


class QuestionFullView(View):
    """Renders full question view"""

    def get(self, request, *args, **kwargs):
        view = QuestionDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = QuestionAnswerFormView.as_view()
        return view(request, *args, **kwargs)


class QuestionCreateView(LoginRequiredMixin, generic.CreateView):
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


class TagsView(generic.ListView):
    """Renders tags table."""

    template_name: str = "questions/tags.html"
    context_object_name: str = "tags_list"

    def get_queryset(self) -> QuerySet[Tag]:
        """Return the last 10 published tags."""

        return Tag.objects.filter(created_at__lte=timezone.now()).order_by(
            "-created_at"
        )[:10]
