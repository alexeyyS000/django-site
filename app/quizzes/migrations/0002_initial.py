# Generated by Django 4.2.6 on 2024-02-18 18:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("quizzes", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="test",
            name="author",
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name="test",
            name="tag",
            field=models.ManyToManyField(blank=True, to="quizzes.tag"),
        ),
        migrations.AddField(
            model_name="question",
            name="test",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="quizzes.test"),
        ),
        migrations.AddField(
            model_name="choice",
            name="question",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="quizzes.question"),
        ),
        migrations.AddField(
            model_name="attemptstate",
            name="attempt",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="quizzes.attemptpipeline"),
        ),
        migrations.AddField(
            model_name="attemptstate",
            name="question",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="quizzes.question"),
        ),
        migrations.AddField(
            model_name="attemptpipeline",
            name="test",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="quizzes.test"),
        ),
        migrations.AddField(
            model_name="attemptpipeline",
            name="user",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
