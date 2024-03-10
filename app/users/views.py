from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetView
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_protect

from .forms import LoginForm
from .forms import UserAvatarUploadForm
from .forms import UserCreationForm
from .models import User
from .tasks import send_message
from .utils.general import CustomPasswordResetForm
from .utils.general import email_authenticate
from .utils.general import generate_confirm_link
from .utils.general import generate_token
from .utils.general import get_cache
from .utils.general import set_verification_token


class RegisterUserView(View):
    template_name = "registration/register.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        context = {"form": UserCreationForm}
        return render(request, self.template_name, context)

    @method_decorator(csrf_protect)
    def post(self, request: HttpRequest) -> HttpResponseRedirect | HttpResponse:
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            password = form.cleaned_data.get("password1")
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            user = authenticate(username=username, password=password)
            token = generate_token()
            set_verification_token(
                token, settings.USER_CONFIRMATION_TIMEOUT, settings.USER_CONFIRMATION_KEY, **{"user_id": user.id}
            )
            confirm_link = generate_confirm_link(request, token)
            send_message.delay(
                None,
                "please confirm your eamail",
                _(f"follow this link %s \n" f"to confirm! \n" % confirm_link),
                None,
                [
                    email,
                ],
            )
            login(request, user)
            return redirect("home")
        context = {"form": form}
        return render(request, self.template_name, context)


class ProfileView(LoginRequiredMixin, View):
    template_name = "users/profile.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        context = {"form": AuthenticationForm}
        return render(request, self.template_name, context)


class ImageUploadView(LoginRequiredMixin, View):
    template_name = "users/imgload.html"

    def post(self, request: HttpRequest) -> HttpResponse:
        form = UserAvatarUploadForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            img_obj = form.instance
            context = {"form": form, "img_obj": img_obj}
            return render(request, self.template_name, context)
        context = {"form": form}
        return render(request, self.template_name, context)

    def get(self, request: HttpRequest) -> HttpResponse:
        form = UserAvatarUploadForm()
        context = {"form": form}
        return render(request, self.template_name, context)


class LoginView(View):
    template_name = "registration/login.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        context = {"form": LoginForm}
        return render(request, self.template_name, context)

    @method_decorator(csrf_protect)
    def post(self, request: HttpRequest) -> HttpResponseRedirect | HttpResponse:
        form = LoginForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get("password")
            email = form.cleaned_data.get("email")
            user = email_authenticate(email=email, password=password)
            login(request, user)
            return redirect("home")
        context = {"form": form}
        return render(request, self.template_name, context)


def register_confirm(request: HttpRequest, token: str) -> HttpResponseRedirect:
    redis_key = settings.USER_CONFIRMATION_KEY.format(token=token)
    user_info = get_cache(redis_key)

    if user_id := user_info.get("user_id"):
        user = get_object_or_404(User, id=user_id)
        user.is_active_email = True
        user.save(update_fields=["is_active_email"])
        return redirect(to=reverse_lazy("users:profile"))
    else:
        return redirect(to=reverse_lazy("users:signup"))


class CustomPasswordResetView(PasswordResetView):
    email_template_name = "emails/password_reset_email.html"
    success_url = reverse_lazy("users:password_reset_done")
    form_class = CustomPasswordResetForm


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    success_url = reverse_lazy("users:password_reset_complete")
