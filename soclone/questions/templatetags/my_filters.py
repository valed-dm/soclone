"""Django customized filters for use in templates."""
import html
import re
from datetime import timedelta

from django import template

register = template.Library()


@register.filter
def timedelta_readable(value: timedelta) -> str:
    """Format a timedelta to be human-readable."""
    if value is None:
        return "Unmodified"

    days: int = value.days
    hours, remainder = divmod(value.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    ending: str = " ago"

    if days > 0:
        string = f"{days} day{'s' if days > 1 else ''}" + ending
    else:
        string = f"{hours:02}:{minutes:02}:{seconds:02}" + ending

    return string


@register.filter
def contains_html(text):
    pattern = r"<[^>]+>"
    return bool(re.search(pattern, text))


@register.filter
def html_parser(data: str) -> str:
    """Converts html string."""

    if contains_html(data):
        unicode_str = html.unescape(data)
        return html.escape(unicode_str)

    return data
