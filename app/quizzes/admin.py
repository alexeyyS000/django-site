from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminTimeWidget
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Choice
from .models import Question
from .models import Tag
from .models import Test


class EditLinkToInlineObject(object):
    def edit_link(self, instance):
        url = reverse("admin:%s_%s_change" % (instance._meta.app_label, instance._meta.model_name), args=[instance.pk])
        if instance.pk:
            return mark_safe('<a href="{u}">edit</a>'.format(u=url))
        else:
            return ""


class TagAdmin(admin.ModelAdmin):
    list_display = ["name"]
    fieldsets = [
        (None, {"fields": ["name"]}),
    ]


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionInline(EditLinkToInlineObject, admin.TabularInline):
    model = Question
    extra = 1
    readonly_fields = ("edit_link",)


# class StopAdminForm(forms.ModelForm):
#     list_display = ["name", ]
#     fieldsets = [
#         (None, {"fields": ["name", "description", "tag", "time_for_complite"]}),
#     ]
#     class Meta:
#         model = Test
#         widgets = {
#         'time_for_complite': AdminTimeWidget(),
#         }
#         fields = '__all__'


class TestAdmin(admin.ModelAdmin):
    list_display = [
        "name",
    ]
    fieldsets = [
        (None, {"fields": ["name", "description", "tag", "time_for_complete"]}),
    ]
    inlines = [QuestionInline]
    # widgets = {
    # 'time_for_complite': AdminTimeWidget(),
    # }


class QuestionAdmin(admin.ModelAdmin):
    list_display = ["question_text", "test"]
    fieldsets = [
        (None, {"fields": ["question_text", "test"]}),
    ]
    inlines = [ChoiceInline]


admin.site.register(Question, QuestionAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(Tag, TagAdmin)
