"""Forms for the questions app."""
from django import forms

from .models import Answer
from .models import Question
from .models import Tag


class QuestionForm(forms.ModelForm):
    """Form for creating Question"""

    class Meta:
        model = Question
        fields = ["title", "problem", "effort", "tags"]

    title = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Enter question title", "class": "form-control"}
        )
    )

    problem = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "placeholder": "What are the details of your problem?\n"
                "Introduce the problem and expand on what you put in the title.\n"
                "Minimum 20 characters.",
                "class": "form-control",
            }
        )
    )

    effort = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "placeholder": "What did you try and what were you expecting?\n"
                "Describe what you tried, what you expected to happen, "
                "and what actually resulted.\n"
                "Minimum 20 characters.",
                "class": "form-control",
            }
        )
    )

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all().order_by("name"),
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
        required=False,
    )


class AnswerForm(forms.ModelForm):
    """Form for creating answers."""

    class Meta:
        model = Answer
        fields = ["body"]

    body = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "placeholder": "Give a brief description of underlying conditions.\n"
                "Propose some clues, methods or attach code samples.\n"
                "Minimum 20 characters.",
                "class": "form-control",
            }
        )
    )
