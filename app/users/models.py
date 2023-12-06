# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.dispatch import receiver
from django_countries.fields import CountryField

from .formatChecker import (
    SizeRestrictedImageField,  # не получилось поместить класс в utils так как происходит ошибка переопределения user так как он там используется
)


class Country(models.Model):
    country = CountryField()


class User(AbstractUser):
    LANGUAGE_CHOICE = [("EN", "en"), ("RU", "ru")]
    avatar = SizeRestrictedImageField(max_upload_size=10485760, null=True)
    birthday = models.DateField(null=True)
    is_active_email = models.BooleanField(default=False)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICE, default="EN")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, default=None)
    updated = models.DateTimeField(auto_now=True)


@receiver(models.signals.pre_save, sender=User)
def delete_file_on_change_extension(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_avatar = User.objects.get(pk=instance.pk).avatar
        except User.DoesNotExist:
            return
        else:
            new_avatar = instance.avatar
            print(new_avatar, old_avatar)
            if (
                old_avatar and new_avatar and old_avatar.url != new_avatar.url
            ):  # как проработать ситуацию удаления если вотография имеет то же название или она же
                old_avatar.delete(save=False)


@receiver(models.signals.pre_delete, sender=User)
def delete_file_on_delete_extension(sender, instance, **kwargs):
    if instance.pk:
        try:
            avatar = User.objects.get(pk=instance.pk).avatar
        except User.DoesNotExist:
            return
        else:
            avatar.delete(save=False)
