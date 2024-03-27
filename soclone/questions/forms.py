"""Forms for the questions app."""
import nh3
from django import forms
from tinymce.widgets import TinyMCE

from .models import Answer
from .models import Question
from .models import Tag
from .utils.remove_tags import remove_tags


class HtmlSanitizedCharField(forms.CharField):
    """Ammonia HTML sanitization library protected attributes."""

    min_length = 20

    def to_python(self, value):
        """Protects against malicious code in user input"""
        value = super().to_python(value)
        if value not in self.empty_values:
            value = nh3.clean(value)
        return value

    def clean(self, value):
        """Validates that the input is 20 characters long."""
        value_length = len(remove_tags(value))
        required = "This field is required."
        short = f"Description is too short. Min length 20, got {value_length}."
        if value_length < self.min_length:
            raise forms.ValidationError(required if value_length == 0 else short)
        return super().clean(value)


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

    problem = HtmlSanitizedCharField(
        widget=TinyMCE(
            attrs={
                "placeholder": "What are the details of your problem?\n"
                "Introduce the problem and expand on what you put in the title.\n"
                "Minimum 20 characters.",
                "class": "form-control",
            }
        ),
        required=True,
        min_length=20,
    )

    effort = HtmlSanitizedCharField(
        widget=TinyMCE(
            attrs={
                "placeholder": "What did you try and what were you expecting?\n"
                "Describe what you tried, what you expected to happen, "
                "and what actually resulted.\n"
                "Minimum 20 characters.",
                "class": "form-control",
            }
        ),
        required=True,
        min_length=20,
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

    body = HtmlSanitizedCharField(
        widget=TinyMCE(
            attrs={
                "placeholder": "Give a brief description of underlying conditions.\n"
                "Propose some clues, methods or attach code samples.\n"
                "Minimum 20 characters.",
                "class": "form-control",
            }
        ),
        required=True,
        min_length=20,
    )
