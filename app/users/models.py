# Create your models here.
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_countries.fields import CountryField


class Country(models.Model):
    country = CountryField()


class Profile(models.Model):
    LANGUAGE_CHOICE = [("EN", "en"), ("RU", "ru")]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(null=True)
    birthday = models.DateField(
        null=True, default=None
    )  # не получается обойтись без default, изза созания профиля после юзера один null=Truе не помогает
    is_active_email = models.BooleanField(default=False)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICE, default="EN")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, default=None)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()
