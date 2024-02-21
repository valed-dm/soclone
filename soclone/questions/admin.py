from django.contrib import admin

from .models import Question
from .models import Tag

admin.site.register(Question)
admin.site.register(Tag)
