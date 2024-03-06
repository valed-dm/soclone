"""Questions middleware."""
import re

from .models import Question
from .models import QuestionsViewsIP
from .models import QuestionUniqueViewsStatistics


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
        Counts question statistic using authenticated user.
        When user is anonymous ip address serves as base parameter.
        """
        response = self.get_response(request)
        path: str = request.path
        rx = re.compile(r"^/questions/(?P<pk>\d+)/$")
        if rx.match(path):
            # AnonymousUser object has id=None and pk=None
            user = request.user if request.user.is_authenticated else None
            pk = int(re.search("\\d+", path)[0])
            ip_address: str = ipaddress(request)

            question = Question.objects.get(id=pk)
            # Keeps unique user-question-ip-date data for possible future analysis
            QuestionsViewsIP.objects.update_or_create(
                # AnonymousUser object is erroneous here and is replaced by None
                user=user,
                question=question,
                ip_address=ip_address,
            )

            ip = QuestionsViewsIP.objects.filter(ip_address=ip_address).first()

            # Collects question-user or question-ip pairs
            if user:
                QuestionUniqueViewsStatistics.objects.update_or_create(
                    question=question, user=user
                )
            else:
                QuestionUniqueViewsStatistics.objects.update_or_create(
                    question=question, ip=ip
                )

        return response
