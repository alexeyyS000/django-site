from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from .models import Country
from .models import User
from .utils import email_authenticate


class UserCreationForm(forms.ModelForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=256,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    country = CountryField(null=True, blank=True).formfield()
    language = forms.ChoiceField(choices=User.LANGUAGE_CHOICE)

    birthday = forms.DateField(input_formats=["%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"])

    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )
    error_messages = {
        "password_mismatch": _("The two password fields didn’t match."),
    }

    first_name = forms.CharField(required=True)

    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "birthday", "language")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        email_exists = User.objects.filter(email=email).first()
        if email_exists:
            msg = "This email is already exist"
            self.add_error("email", msg)
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        return password2

    def save(self, commit=True):
        instance = super(UserCreationForm, self).save(commit=False)
        instance.set_password(self.cleaned_data["password1"])
        country = self.cleaned_data.get("country")
        instance.country = Country.objects.get(country=country)
        if commit:
            instance.save()
        return instance


class UserAvatarUploadForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("avatar",)

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if avatar:
            if "image" != avatar.content_type[:5]:
                raise ValidationError("it is not image type")

            if avatar.size > 10000:
                raise ValidationError("Image file too large ( > 10mb )")

            return avatar

        else:
            raise ValidationError("Couldn't read uploaded image")


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
