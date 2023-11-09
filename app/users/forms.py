from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Profile


User = get_user_model()


class UserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")


class ImageLoad(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("avatar_url",)


# class CustomAuthenticationForm(AuthenticationForm):
#     email = forms.EmailField(widget=forms.TextInput(attrs={"autofocus": True}))


class CustomLoginform(forms.Form):  # не смог переопределить LoginForm
    email = forms.CharField()
    password = forms.CharField(
        widget=forms.PasswordInput,
        error_messages={"required": "Please Enter your password"},
    )
