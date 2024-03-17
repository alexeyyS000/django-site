# Generated by Django 4.2.6 on 2024-02-18 18:04

from django.contrib.auth.management import create_permissions
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import migrations


def force_create_permissions(apps, schema_editor):
    """creates permissions without waiting for post_migrate signal"""
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None


def grant_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    moderator_group, exisit = Group.objects.get_or_create(name="moderator")
    PERMISSIONS_LIST = [
        ("quizzes", "Test"),
        ("quizzes", "Tag"),
        ("quizzes", "Question"),
        ("quizzes", "Choice"),
        ("quizzes", "AttemptPipeline"),
    ]
    for package, model_name in PERMISSIONS_LIST:
        model = apps.get_model(package, model_name)
        content_type = ContentType.objects.get_for_model(model)
        test_permission = Permission.objects.filter(content_type=content_type).values_list("id", flat=True)
        moderator_group.permissions.add(*test_permission)


def revoke_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    moderator_group = Group.objects.get(name="moderator")
    moderator_group.clean()
    moderator_group.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_user_done_tests"),
    ]

    operations = [
        migrations.RunPython(force_create_permissions, migrations.RunPython.noop),
        migrations.RunPython(grant_permissions, reverse_code=revoke_permissions),
    ]
