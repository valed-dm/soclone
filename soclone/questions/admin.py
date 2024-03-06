from django.contrib import admin

from .models import Answer
from .models import AnswerVote
from .models import Question
from .models import QuestionsViewsIP
from .models import QuestionUniqueViewsStatistics
from .models import QuestionVote
from .models import Tag

admin.site.register(Answer)
admin.site.register(AnswerVote)
admin.site.register(Question)
admin.site.register(QuestionUniqueViewsStatistics)
admin.site.register(QuestionsViewsIP)
admin.site.register(QuestionVote)
admin.site.register(Tag)
