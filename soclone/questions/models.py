"""Questions models."""
from django.core.validators import MinLengthValidator
from django.db import models

from soclone.users.models import User

validators: list = [
    MinLengthValidator(
        limit_value=20, message="Description must be 20 characters or more."
    )
]


class TimestampMixin(models.Model):
    """Timestamp mixin."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserMixin(models.Model):
    """User mixin."""

    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class AppraisalMixin(UserMixin):
    """Appraisal mixin."""

    is_useful = models.BooleanField(blank=True, null=True)

    class Meta:
        abstract = True


class Tag(UserMixin, TimestampMixin):
    """Tag model."""

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.name!r}"


class Question(UserMixin, TimestampMixin):
    """Question model."""

    title = models.CharField(max_length=200, unique=True)
    problem = models.TextField(unique=True, validators=validators)
    effort = models.TextField(unique=True, validators=validators)
    tags = models.ManyToManyField(Tag, blank=True, default=None)

    def __str__(self):
        return f"{self.title[:20]!r}.."


class Answer(UserMixin, TimestampMixin):
    """Answer model."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    body = models.TextField(unique=True, validators=validators)

    def __str__(self):
        return f"reply to {self.question.title[:20]!r}.."


class QuestionVote(AppraisalMixin, TimestampMixin):
    """Question vote model."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["question", "user", "is_useful"], name="unique_question_vote"
            )
        ]

    def __str__(self):
        return f"vote for question {self.question.title[:20]!r}.."


class AnswerVote(AppraisalMixin, TimestampMixin):
    """Answer vote model."""

    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["answer", "user", "is_useful"], name="unique_answer_vote"
            )
        ]

    def __str__(self):
        return f"vote for answer to {self.answer.question.title[:20]!r}.."


class QuestionsViewsIP(UserMixin, TimestampMixin):
    """Questions IP collection."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=50)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["question", "user", "ip_address"],
                name="unique_question_user_ip_view",
            )
        ]

    def __str__(self):
        return self.ip_address


class QuestionUniqueViewsStatistics(UserMixin):
    """Question views statistic model."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    ip = models.ForeignKey(QuestionsViewsIP, null=True, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["question", "user"], name="unique_question_user_view"
            ),
            models.UniqueConstraint(
                fields=["question", "ip"], name="unique_question_ip_view"
            ),
        ]

    def __str__(self):
        return (
            f"question {self.question.title[:20]!r} "
            f"user {self.user.email if self.user else self.ip.ip_address} view"
        )
