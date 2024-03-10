"""Questions middleware."""
import re
from typing import TYPE_CHECKING
from typing import Any

from .models import Question
from .models import QuestionsViewsIP
from .models import QuestionUniqueViewsStatistics

if TYPE_CHECKING:
    from django.contrib.auth.models import User


def ipaddress(request) -> str:
    """Get ip address from request object."""
    user_ip: str = request.headers.get("x-forwarded-for")
    if user_ip:
        ip: str = user_ip.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


class QuestionViewMiddleware:
    """Adds unique views to question statistic."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Views engine.
        Counts question views statistic based on user authenticated.
        When user is anonymous ip address serves as user identity.
        """
        response: Any = self.get_response(request)

        path: str = request.path
        rx = re.compile(r"^/questions/(?P<pk>\d+)/$")

        if rx.match(path):
            # AnonymousUser object has id=None and pk=None
            # AnonymousUser is replaced by None
            user: User | None = request.user if request.user.is_authenticated else None
            pk = int(re.search("\\d+", path)[0])
            ip_address: str = ipaddress(request)

            question: Question = Question.objects.get(id=pk)
            # Keeps unique user-question-ip-date data for possible future analysis
            QuestionsViewsIP.objects.update_or_create(
                # AnonymousUser object would be erroneous here
                user=user,
                question=question,
                ip_address=ip_address,
            )

            # Collects question-user or question-ip pairs
            if user:
                QuestionUniqueViewsStatistics.objects.update_or_create(
                    question=question, user=user
                )
            else:
                ip: QuestionsViewsIP = QuestionsViewsIP.objects.filter(
                    ip_address=ip_address
                ).first()
                QuestionUniqueViewsStatistics.objects.update_or_create(
                    question=question, ip=ip
                )

        return response
