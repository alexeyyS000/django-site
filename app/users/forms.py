from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Profile
from .utils import email_authenticate


class UserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=256,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        UserModel = get_user_model()
        if UserModel.objects.filter(email=email).first() is not None:
            msg = "This email is already exist"
            self.add_error("email", msg)
        return email


class UserAvatarUploadForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("avatar_url",)


class LoginForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        max_length=256,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )

    password = forms.CharField(
        widget=forms.PasswordInput,
        error_messages={"required": "Please Enter your password"},
    )

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email and password:
            user = email_authenticate(email=email, password=password)
            if user is None:
                raise ValidationError("incorrect email or password")
            # else:
            #     login(self.request, user) хочется сделать логин прям здесть, пока не знаю как правильно передать request
        return self.cleaned_data
