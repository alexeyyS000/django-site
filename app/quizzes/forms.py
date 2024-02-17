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
        if answers == right_answers:
            AttemptState.objects.get_or_create(
                attempt=current_attempt, question=self.question, defaults={"answer": True}
            )
        else:
            AttemptState.objects.get_or_create(
                attempt=current_attempt, question=self.question, defaults={"answer": False}
            )
