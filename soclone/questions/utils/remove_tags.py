import html
import re


def remove_tags(data: str) -> str:
    """Removes tags from a html string"""
    unescaped = html.unescape(data)
    remover = re.compile("<.*?>")
    return re.sub(remover, "", unescaped)
