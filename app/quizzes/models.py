from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

UserModel = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=32, null=False)

    def __str__(self):
        return self.name


class Test(models.Model):
    name = models.CharField(max_length=32, null=False)
    description = models.CharField(max_length=256, null=False)
    tag = models.ManyToManyField(Tag, blank=True)
    time_for_complete = models.DurationField(null=False)
    attempts = models.IntegerField(null=False, validators=[MinValueValidator(1)])
    author = models.ForeignKey("users.User", on_delete=models.RESTRICT)
    created = models.DateTimeField(auto_now_add=True)
    is_hidden = models.BooleanField(default=True)
    has_first_attempt = models.BooleanField(null=False, default=False)

    def __str__(self):
        return self.name


class Question(models.Model):
    test = models.ForeignKey(Test, related_name="questions", on_delete=models.CASCADE)
    text = models.CharField(max_length=256)
    order = models.PositiveIntegerField(default=0, blank=False, null=False, db_index=True)

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


class AttemptPipeline(models.Model):
    time_start = models.DateTimeField(auto_now_add=True)
    time_end = models.DateTimeField(null=True)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    is_attempt_completed = models.BooleanField(default=False)


class AttemptState(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(null=True)
    attempt = models.ForeignKey(AttemptPipeline, related_name="pipelines", on_delete=models.CASCADE)
    is_right = models.BooleanField(default=False)
