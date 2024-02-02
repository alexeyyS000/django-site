from django.contrib import admin

from .models import Choice
from .models import Question
from .models import Tag
from .models import Test
from .utils.utils import EditLinkToInlineObjectMixin


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name"]
    fields = ["name"]


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionInline(EditLinkToInlineObjectMixin, admin.TabularInline):
    model = Question
    extra = 1
    readonly_fields = ("edit_link",)



@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = [
        "name",
    ]
    fields = ["name", "description", "tag", "time_for_complete"]
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["text", "test"]
    fields = ["text", "test"]
    inlines = [ChoiceInline]


