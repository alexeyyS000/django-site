# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from django_countries.fields import CountryField


class Country(models.Model):
    country = CountryField()


class User(AbstractUser):
    LANGUAGE_CHOICE = [("EN", "en"), ("RU", "ru")]  # не знаю стоит ли выносить константу в settings
    avatar = models.ImageField(null=True)
    birthday = models.DateField(null=True)
    is_active_email = models.BooleanField(default=False)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICE, default="EN")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, default=None)
    updated = models.DateTimeField(auto_now=True)
