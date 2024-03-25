from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Case
from django.db.models import Count
from django.db.models import F
from django.db.models import IntegerField
from django.db.models import When

UserModel = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=32, null=False)

    def __str__(self):
        return self.name


class TestManager(models.Manager):
    def with_count_attempts_used(self, user):
        return self.annotate(
            attempts_used=Count(
                Case(
                    When(attemptpipeline__user=user, then=1),
                    output_field=IntegerField(),
                )
            )
        )


class Test(models.Model):
    name = models.CharField(max_length=32, null=False)
    description = models.CharField(max_length=256, null=False)
    tag = models.ManyToManyField(Tag, blank=True)
    time_for_complete = models.DurationField(null=False, validators=[MaxValueValidator(timedelta(minutes=59))])
    attempts = models.IntegerField(null=False, validators=[MinValueValidator(1)])
    author = models.ForeignKey("users.User", on_delete=models.RESTRICT)
    created = models.DateTimeField(auto_now_add=True)
    is_hidden = models.BooleanField(default=True)
    has_first_attempt = models.BooleanField(null=False, default=False)
    objects = TestManager()

    def __str__(self):
        return self.name


class QuestionManager(models.Manager):
    def with_quantity_right_answers(self):
        return self.annotate(quantity_right_answers=Count(Case(When(choices__right_answer=True, then=1))))


class Question(models.Model):
    test = models.ForeignKey(Test, related_name="questions", on_delete=models.CASCADE)
    text = models.CharField(max_length=256)
    order = models.PositiveIntegerField(default=0, blank=False, null=False, db_index=True)
    objects = QuestionManager()

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(Question, related_name="choices", on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=256)
    right_answer = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text


class AttemptPipelineManager(models.Manager):
    def with_time_took(self):
        return self.annotate(time_took=F("time_end") - F("time_start") if F("time_end") else None)


class AttemptPipeline(models.Model):
    time_start = models.DateTimeField(auto_now_add=True)
    time_end = models.DateTimeField(null=True)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    is_attempt_completed = models.BooleanField(default=False)
    objects = AttemptPipelineManager()


class AttemptState(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.JSONField("answer_id", null=True)
    attempt = models.ForeignKey(AttemptPipeline, related_name="pipelines", on_delete=models.CASCADE)
    is_right = models.BooleanField(default=False)
