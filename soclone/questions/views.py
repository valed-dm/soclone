"""Views for the questions app."""
from datetime import timedelta
from typing import TYPE_CHECKING
from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Case
from django.db.models import Count
from django.db.models import F
from django.db.models import OuterRef
from django.db.models import Subquery
from django.db.models import When
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect
from django.http import QueryDict
from django.shortcuts import redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views import generic
from django.views.generic.detail import SingleObjectMixin

from soclone.questions.forms import AnswerForm
from soclone.questions.forms import QuestionForm
from soclone.questions.models import Answer
from soclone.questions.models import AnswerVote
from soclone.questions.models import Question
from soclone.questions.models import QuestionUniqueViewsStatistics
from soclone.questions.models import QuestionVote
from soclone.questions.models import Tag
from soclone.questions.utils.xss_guard import xss_guard
from soclone.questions.utils.xss_guard import xss_multiple_guard

if TYPE_CHECKING:
    from django.db.models.functions import datetime


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

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Enrich context data with statistics and answer form."""
        context: dict[str, Any] = super().get_context_data(**kwargs)
        q: Question = context["question"]
        cat: datetime = q.created_at
        uat: datetime = q.updated_at
        views: int = QuestionUniqueViewsStatistics.objects.filter(question=q.id).count()
        answers: QuerySet[Answer] = (
            Answer.objects.filter(question=q.id)
            .select_related("user")
            .annotate(
                rating=Subquery(
                    AnswerVote.objects.values("is_useful")
                    .filter(answer=OuterRef("id"))
                    .annotate(
                        diff=(
                            Count(Case(When(is_useful=True, then=1)))
                            - Count(Case(When(is_useful=False, then=1)))
                        )
                    )
                    .values("diff")
                )
            )
            .order_by("-created_at")
        )
        q_rating: dict[str, int] = QuestionVote.objects.filter(question=q.id).aggregate(
            rating=(
                Count(Case(When(is_useful=True, then=1)))
                - Count(Case(When(is_useful=False, then=1)))
            )
        )

        context["qid"] = q.id
        context["posed"] = timezone.now() - cat
        context["modified"] = (
            (timezone.now() - uat) if (uat - cat) > timedelta(seconds=1) else None
        )
        context["views"] = views
        context["q_rating"] = q_rating["rating"]
        context["answers_qty"] = answers.count()
        context["answers"] = answers
        context["answer_form"] = AnswerForm()

        # to show AnswerForm errors in a Django style
        answer_form_invalid = self.request.session.get("answer_form_invalid")
        if answer_form_invalid:
            answer_form_body = self.request.session.get("answer_form_body")
            xss_safe, data = xss_guard(answer_form_body)
            if not xss_safe:
                messages.error(self.request, message="Answer malicious code dropped")
            context["answer_form"] = AnswerForm(QueryDict(f"body={data}"))
            # AnswerForm errors values are dropped
            self.request.session["answer_form_invalid"] = False
            self.request.session["answer_form_body"] = None

        return context


class QuestionAnswerFormView(SingleObjectMixin, LoginRequiredMixin, generic.FormView):
    """Renders answer form for question."""

    model = Answer
    form_class = AnswerForm

    def post(self, request, *args, **kwargs):
        """Enables post request for question."""
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        body_text = form["body"].value()
        self.request.session["answer_form_invalid"] = True
        self.request.session["answer_form_body"] = body_text
        return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):
        """
        Enables custom AnswerForm validation.
        Saves Answer to db manually as it's not generic.CreateView.
        """
        answer = Answer(
            user=self.request.user,
            question=Question.objects.get(id=self.kwargs.get("pk")),
            body=self.request.POST["body"],
        )
        try:
            answer.save()
            messages.success(self.request, "The answer was added successfully.")
        except IntegrityError:
            messages.error(self.request, "Identical answer already exists.")
        return super().form_valid(form)

    def get_success_url(self):
        """Returns successful view url"""
        return reverse("questions:question", kwargs={"pk": self.kwargs.get("pk")})


class QuestionFullView(View):
    """
    Combines QuestionDetailView and QuestionAnswerFormView in a single view.
    """

    @staticmethod
    def get(request, *args, **kwargs):
        """Defines GET request view"""
        view = QuestionDetailView.as_view()
        return view(request, *args, **kwargs)

    @staticmethod
    def post(request, *args, **kwargs):
        """Defines POST request view"""
        view = QuestionAnswerFormView.as_view()
        return view(request, *args, **kwargs)


class QuestionCreateView(LoginRequiredMixin, generic.CreateView):
    """Creates a question."""

    # CreateView class uses the question_form.html template from the templates/questions
    # with the following naming convention: model_form.html
    model = Question
    form_class = QuestionForm
    success_url = reverse_lazy("questions:questions")

    def form_invalid(self, form):
        guarded = xss_multiple_guard(
            request=self.request, form=form, fields=("problem", "effort")
        )
        qd = self.request.POST.copy()
        qd["problem"] = guarded.get("problem")
        qd["effort"] = guarded.get("effort")
        return super().form_invalid(QuestionForm(qd))

    def form_valid(self, form):
        """
        Enables custom QuestionForm validation.
        Bounds user instance to the question created.
        """
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


@login_required
def rating(request, **kwargs):
    """
    Rating engine.
    Provides positive or negative voting for a question or an answer.
    Eliminates code duplication when rating statistics are being recorded.
    Redirects to question view.
    """
    q_pk: int = kwargs.get("q_pk")
    a_pk: int | None = kwargs.get("a_pk", None)
    pk: tuple[int | None, int] = a_pk, q_pk
    useful: int = kwargs.get("useful")
    canister: dict = {"user": request.user}
    option: int = 0 if a_pk else 1

    obj_model: tuple = Answer, Question
    votes_model: tuple = AnswerVote, QuestionVote
    vote_attr: tuple[str, str] = "answer", "question"

    obj: Answer | Question = obj_model[option].objects.get(id=pk[option])
    canister[vote_attr[option]] = obj

    obj_rating: AnswerVote | QuestionVote = (
        votes_model[option]
        .objects.filter(**canister)
        .update(is_useful=useful, updated_at=timezone.now())
    )
    if not obj_rating:
        votes_model[option].objects.create(**canister, is_useful=bool(useful))

    return redirect("questions:question", pk=q_pk)
