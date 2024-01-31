import datetime

from django.contrib.auth import get_user_model
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
    time_for_complete = models.TimeField(null=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def time_in_seconds(self):
        return (self.time_for_complete.hour * 60 + self.time_for_complete.minute) * 60 + self.time_for_complete.second

    def time_to_timedelta(self):
        return datetime.timedelta(
            hours=self.time_for_complete.hour,
            minutes=self.time_for_complete.minute,
            seconds=self.time_for_complete.second,
            microseconds=self.time_for_complete.microsecond,
        )


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
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.BooleanField()
    # time_start = models.TimeField(null=False)#можно ли не создавать таблицу ради этой строки и прописать здесь time_start


class TestPipeline(models.Model):
    time_start = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        UserModel, on_delete=models.CASCADE
    )  # не знаю нужен ли тут ForeignKey или можно просто int id
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
