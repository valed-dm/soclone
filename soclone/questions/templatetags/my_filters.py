"""Django customized filters for use in templates."""
from datetime import timedelta

from django import template

register = template.Library()


@register.filter
def timedelta_readable(value: timedelta) -> str:
    """Format a timedelta to be human-readable."""
    days: int = value.days
    hours, remainder = divmod(value.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    string = ""
    if days > 0:
        string += f"{days} day{'s' if days > 1 else ''}, "
    string += f"{hours:02}:{minutes:02}:{seconds:02}"

    return string
