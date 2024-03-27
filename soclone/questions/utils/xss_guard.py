"""Guards """
import html

import nh3
from django.contrib import messages


def xss_guard(data: str) -> tuple[bool, str]:
    """HTML string XSS attack single field guard"""
    unescaped = html.unescape(data)
    nh3_cleaned_string = nh3.clean(unescaped)
    is_xss_safe = len(unescaped) == len(nh3_cleaned_string)
    return is_xss_safe, nh3_cleaned_string


def xss_multiple_guard(request, form, fields: tuple) -> dict[str, str]:
    """HTML string XSS attack multiple field guard"""
    cleaned_strings: dict = {}
    for field in fields:
        html_string = form[field].value()
        is_xss_safe, nh3_cleaned_string = xss_guard(html_string)
        if not is_xss_safe:
            messages.error(request, message=f"{field} malicious code dropped")
        cleaned_strings[field] = nh3_cleaned_string
    return cleaned_strings
