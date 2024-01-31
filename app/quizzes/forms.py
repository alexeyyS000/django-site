from django import forms

from .models import Choice
from .models import TestPipeline
from .models import TestState
from .utils.utils import is_time_up
from .utils.utils import time_to_timedelta


class AnswerQuestionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        try:
            self.question = kwargs.pop("question")
        except KeyError:
            self.question = None
        super(AnswerQuestionForm, self).__init__(*args, **kwargs)
        if self.question:
            self.fields["choices"] = forms.MultipleChoiceField(
                choices=[(o.id, str(o)) for o in Choice.objects.filter(question=self.question)],
                widget=forms.CheckboxSelectMultiple,
            )

    def save(self, user, test):
        answers = {int(x) for x in self.cleaned_data.get("choices")}
        right_answers = {x.id for x in Choice.objects.filter(question=self.question, right_answer=True)}
        if answers == right_answers:
            TestState.objects.get_or_create(user_id=user.id, test=test, question=self.question, defaults={"answer": True})
        else:
            TestState.objects.get_or_create(user=user, test=test, question=self.question, defaults={"answer": False})


class FilterForm(forms.Form):
    ORDER_CHOICES = (
        (None, "----"),
        ("name", "name"),
        ("create_date", "create date"),
    )
    order_field = forms.ChoiceField(choices=ORDER_CHOICES, required=False)
    find_field = forms.CharField(required=False)
    page_size = forms.IntegerField(required=True)
    page_number = forms.IntegerField(required=True)


class PaginationForm(forms.Form):
    page_size = forms.IntegerField(required=True)
    page_number = forms.IntegerField(required=True)