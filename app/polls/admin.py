from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Choice
from .models import Question
from .models import Test


class EditLinkToInlineObject(object):
    def edit_link(self, instance):
        url = reverse("admin:%s_%s_change" % (instance._meta.app_label, instance._meta.model_name), args=[instance.pk])
        if instance.pk:
            return mark_safe('<a href="{u}">edit</a>'.format(u=url))
        else:
            return ""


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionInline(EditLinkToInlineObject, admin.TabularInline):
    model = Question
    inlines = [ChoiceInline]
    extra = 1
    readonly_fields = ("edit_link",)


class TestAdmin(admin.ModelAdmin):
    list_display = ["name", "tags"]
    fieldsets = [
        (None, {"fields": ["name", "description", "tags", "time_for_complite"]}),
    ]
    inlines = [QuestionInline]


class QuestionAdmin(admin.ModelAdmin):
    list_display = ["question_text", "test"]
    fieldsets = [
        (None, {"fields": ["question_text", 'test']}),
    ]
    inlines = [ChoiceInline]


admin.site.register(Question, QuestionAdmin)
admin.site.register(Test, TestAdmin)
