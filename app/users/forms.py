from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from .models import Profile
from .utils import email_authenticate

UserModel = get_user_model()


class UserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=256,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    country = CountryField(null=True, blank=True).formfield()
    language = forms.ChoiceField(choices=Profile.LANGUAGE_CHOICE)

    birthday = forms.DateField(input_formats=["%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"])

    class Meta(UserCreationForm.Meta):
        model = UserModel
        fields = ("username", "email", "first_name", "last_name")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        email_exists = UserModel.objects.filter(email=email).first()
        if email_exists:
            msg = "This email is already exist"
            self.add_error("email", msg)
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if not first_name:
            msg = "enter your first name"
            self.add_error("first_name", msg)
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if not last_name:
            msg = "enter your first name"
            self.add_error("last_name", msg)
        return last_name


class UserAvatarUploadForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("avatar",)


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
        return self.cleaned_data
