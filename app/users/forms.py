from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import Profile


class UserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email")

    def clean_email(self):
        print("in clean_email")
        email = self.cleaned_data.get("email")
        print(email)
        UserModel = get_user_model()
        if UserModel.objects.filter(email=email).first() is not None:
            print("in yslovie")
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
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
        )
    
    password = forms.CharField(
        widget=forms.PasswordInput,
        error_messages={"required": "Please Enter your password"},
    )
