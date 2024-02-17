from adminsortable2.admin import SortableAdminBase
from adminsortable2.admin import SortableStackedInline
from django.contrib import admin

from .models import AttemptPipeline
from .models import AttemptState
from .models import Choice
from .models import Question
from .models import Tag
from .models import Test
from .utils.admin import EditLinkToInlineObjectMixin


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name"]
    fields = ["name"]


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionInline(SortableStackedInline, EditLinkToInlineObjectMixin, admin.TabularInline):
    model = Question
    extra = 1
    readonly_fields = ("link",)


@admin.register(Test)
class TestAdmin(SortableAdminBase, admin.ModelAdmin):
    list_display = ["name", "is_hidden"]
    fields = ["name", "description", "tag", "time_for_complete", "attempts", "is_hidden"]
    inlines = [QuestionInline]
    search_fields = ("name", "tag__name__icontains")

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        super().save_model(request, obj, form, change)


class StateInline(admin.TabularInline):
    model = AttemptState


@admin.register(AttemptPipeline)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ["time_start", "time_end", "user", "test", "is_attempt_completed"]
    search_fields = ("test__name__iexact", "user__username__iexact")
    inlines = [StateInline]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, *args, **kwargs):
        return False


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["text", "test"]
    fields = ["text", "test"]
    inlines = [ChoiceInline]
