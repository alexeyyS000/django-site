from django import forms

from .models import AttemptPipeline
from .models import AttemptState
from .models import Choice


class AnswerQuestionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.question = kwargs.pop("question")
        self.user = kwargs.pop("user")
        self.pipline = kwargs.pop("pipline")
        super(AnswerQuestionForm, self).__init__(*args, **kwargs)
        user_answer = AttemptState.objects.filter(question=self.question, attempt=self.pipline).first()
        if user_answer:
            initial = user_answer.answer["answer_id"]
        else:
            initial = None
        choices = self.question.choices.all()
        if self.question.quantity_right_answers > 1:
            self.fields["choices"] = forms.MultipleChoiceField(
                initial=initial,
                choices=[(o.id, str(o)) for o in choices],
                widget=forms.CheckboxSelectMultiple,
            )
        else:
            self.fields["choices"] = forms.ChoiceField(
                initial=initial,
                choices=[(o.id, str(o)) for o in choices],
                widget=forms.RadioSelect,
            )

    def save(self, user, test):
        current_attempt = AttemptPipeline.objects.get(user=user, test_id=test, is_attempt_completed=False)
        cleaned_data = self.cleaned_data.get("choices")
        answers = [int(x) for x in cleaned_data] if type(cleaned_data) is list else [int(cleaned_data)]
        answers_dict = {int(x) for x in cleaned_data} if type(cleaned_data) is list else {int(cleaned_data)}
        right_answers = {x.id for x in Choice.objects.filter(question=self.question, right_answer=True)}
        AttemptState.objects.create(
            attempt=current_attempt,
            question=self.question,
            answer={"answer_id": answers},
            is_right=answers_dict == right_answers,
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
    tag = forms.CharField(required=False, widget=forms.TextInput(attrs={"filter_field": "tag__name"}))


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
