from django import forms

from .models import AttemptPipeline
from .models import AttemptState
from .models import Choice


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
        current_attempt = AttemptPipeline.objects.get(user=user, test_id=test, is_attempt_completed=False)
        answers = {int(x) for x in self.cleaned_data.get("choices")}
        right_answers = {x.id for x in Choice.objects.filter(question=self.question, right_answer=True)}
        AttemptState.objects.get_or_create(
            attempt=current_attempt, question=self.question, defaults={"answer": answers == right_answers}
        )


class TestFormSearchAdmin(forms.Form):
    name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "filter_method": "__contains",
            }
        ),
    )
    tag = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"filter_field": "tag__name", "filter_method": "__in"})
    )


class AttemptFormSearchAdmin(forms.Form):
    test = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "filter_field": "test__name",
                "filter_method": "__contains",
            }
        ),
    )
    username = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "filter_field": "user__username",
            }
        ),
    )
