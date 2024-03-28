import os

import pytest
from django.core.exceptions import ValidationError
from django.test import TestCase
from tinymce.models import HTMLField

from soclone.questions.models import Question
from soclone.users.models import User


class QuestionModelTests(TestCase):
    """Testing Question model"""

    title_max_length = 200
    nineteen_char = "1234567890123456789"
    twenty_char = "12345678901234567890"

    @classmethod
    def setUpTestData(cls):
        """Creates Question instance for tests."""
        tester = User.objects.create(
            name="tester",
            email="tester@tester.com",
            password=os.environ["TESTER_PASSWORD"],
        )
        cls.question = Question.objects.create(
            user=tester,
            title="Question_1",
            problem="Question_1 Test Problem Description",
            effort="Question_1 Test Effort Description",
        )
        cls.user = User.objects.create(
            name="user",
            email="user@tester.com",
            password=os.environ["USER_PASSWORD"],
        )

    def test_title_label(self):
        """Testing title label attribute."""
        field_label = self.question._meta.get_field("title").verbose_name  # noqa: SLF001
        assert field_label == "title"

    def test_title_max_length(self):
        """Testing title max_length constraint"""
        max_length = self.question._meta.get_field("title").max_length  # noqa: SLF001
        assert max_length == self.title_max_length

    def test_problem_label(self):
        """Testing problem label attribute."""
        field_label = self.question._meta.get_field("problem").verbose_name  # noqa: SLF001
        assert field_label == "problem"

    def test_problem_field_type(self):
        """Testing problem field type."""
        t = type(self.question._meta.get_field("problem"))  # noqa: SLF001
        assert t == HTMLField

    def test_problem_min_length_20(self):
        """
        Testing problem description min_length (20 chars).
        Test string contains 19 chars. This value is not valid.
        """
        question = Question(
            user=self.user,
            title="Question_2",
            problem=self.nineteen_char,
            effort="Question_2 Test Effort Description",
        )
        with pytest.raises(ValidationError):
            question.full_clean()

    def test_problem_length(self):
        """
        Testing problem description string which consists of 20 chars.
        This value is valid.
        """
        question = Question(
            user=self.user,
            title="Question_3",
            problem=self.twenty_char,
            effort="Question_3 Test Effort Description",
        )
        question.full_clean()
        question.save()
        q_obj = Question.objects.get(id=question.id)
        assert self.twenty_char == q_obj.problem

    def test_effort_label(self):
        """Testing effort label attribute."""
        field_label = self.question._meta.get_field("effort").verbose_name  # noqa: SLF001
        assert field_label == "effort"

    def test_effort_field_type(self):
        """Testing effort field type."""
        t = type(self.question._meta.get_field("effort"))  # noqa: SLF001
        assert t == HTMLField

    def test_effort_min_length_20(self):
        """
        Testing effort description min_length (20 chars).
        Test string contains 19 chars. This value is not valid.
        """
        question = Question(
            user=self.user,
            title="Question_4",
            problem="Question_4 Test Problem Description",
            effort=self.nineteen_char,
        )
        with pytest.raises(ValidationError):
            question.full_clean()

    def test_effort_length(self):
        """
        Testing effort description string which consists of 20 chars.
        This value is valid.
        """
        question = Question(
            user=self.user,
            title="Question_5",
            problem="Question_5 Test Problem Description",
            effort=self.twenty_char,
        )
        question.full_clean()
        question.save()
        q_obj = Question.objects.get(id=question.id)
        assert self.twenty_char == q_obj.effort

    def test_tags_label(self):
        """Testing tags label attribute."""
        field_label = self.question._meta.get_field("tags").verbose_name  # noqa: SLF001
        assert field_label == "tags"

    def test_user_label(self):
        """Testing user_label attribute"""
        field_label = self.question._meta.get_field("user").verbose_name  # noqa: SLF001
        assert field_label == "user"

    def test_created_at_label(self):
        """Testing created_at attribute"""
        field_label = self.question._meta.get_field("created_at").verbose_name  # noqa: SLF001
        assert field_label == "created at"

    def test_updated_at_label(self):
        """Testing updated_at attribute"""
        field_label = self.question._meta.get_field("updated_at").verbose_name  # noqa: SLF001
        assert field_label == "updated at"
