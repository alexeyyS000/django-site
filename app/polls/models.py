from django.db import models
from django.contrib.auth import get_user_model
UserModel = get_user_model()

class Test(models.Model):
    name = models.CharField(max_length=32, null=False)
    description = models.CharField(max_length=256, null=False)
    tags = models.CharField(max_length=256, null=True)
    time_for_complite = models.DateTimeField(null=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=256)

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=256)
    right_answer = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text


class TestState(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.BooleanField()