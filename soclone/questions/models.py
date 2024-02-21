"""Questions models."""
from django.core.validators import MinLengthValidator
from django.db import models

validators: list = [
    MinLengthValidator(
        limit_value=20, message="Description must be 20 characters or more."
    )
]


class Tag(models.Model):
    """Tag model."""

    name = models.CharField(max_length=50, unique=True)
    pub_date = models.DateTimeField("date published")

    def __str__(self):
        return f"{self.name!r}"


class Question(models.Model):
    """Question model."""

    title = models.CharField(max_length=200, unique=True)
    problem = models.TextField(
        help_text=(
            "What are the details of your problem?\n"
            "Introduce the problem and expand on what you put in the title."
            "Minimum 20 characters."
        ),
        unique=True,
        validators=validators,
    )
    effort = models.TextField(
        help_text=(
            "What did you try and what were you expecting?\n"
            "Describe what you tried, what you expected to happen, "
            "and what actually resulted. "
            "Minimum 20 characters."
        ),
        unique=True,
        validators=validators,
    )
    pub_date = models.DateTimeField("date published")
    tags = models.ManyToManyField(Tag, related_name="questions", blank=True)

    def __str__(self):
        return f"{self.title!r}"
