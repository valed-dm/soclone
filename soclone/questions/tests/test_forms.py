from django.test import SimpleTestCase

from soclone.questions.forms import HtmlSanitizedCharField


class HtmlSanitizedCharFieldTests(SimpleTestCase):
    field = HtmlSanitizedCharField()

    def test_empty(self):
        result = self.field.to_python("")
        assert result == ""

    def test_allowed_html(self):
        result = self.field.to_python("<strong>Arm</strong>")
        assert result == "<strong>Arm</strong>"

    def test_naughty_html(self):
        result = self.field.to_python(
            "<script src=example.com/evil.js></script><strong>Arm</strong>"
        )
        assert result == "<strong>Arm</strong>"
