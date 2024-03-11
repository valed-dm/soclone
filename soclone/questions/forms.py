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

    problem = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control"}))

    effort = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control"}))

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

    body = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control"}))
