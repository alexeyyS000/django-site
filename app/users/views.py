import uuid

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.mail import EmailMessage
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
from .models import Profile
from .utils import email_authenticate

UserModel = get_user_model()


class RegisterUserView(View):
    template_name = "registration/register.html"

    def get(self, request):
        context = {"form": UserCreationForm, "title": "Registration"}
        return render(request, self.template_name, context)

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            password = form.cleaned_data.get("password1")
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            user = authenticate(username=username, password=password)

            user = UserModel.objects.get(email=email)
            token = uuid.uuid4().hex
            redis_key = settings.USER_CONFIRMATION_KEY.format(token=token)
            cache.set(redis_key, {"user_id": user.id}, timeout=settings.USER_CONFIRMATION_TIMEOUT)

            confirm_link = self.request.build_absolute_uri(
                reverse_lazy("users:register_confirm", kwargs={"token": token})
            )
            message = _(f"follow this link %s \n" f"to confirm! \n" % confirm_link)

            email = EmailMessage("please confirm your eamail", message, to=[email])
            email.send()

            login(request, user)
            return redirect("home")
        context = {"form": form}
        return render(request, self.template_name, context)


class ProfileView(LoginRequiredMixin, View):
    template_name = "profile.html"

    def get(self, request):
        context = {"form": AuthenticationForm, "title": "Profile"}
        return render(request, self.template_name, context)


class ImageUploadView(LoginRequiredMixin, View):
    template_name = "imgload.html"

    def post(self, request):
        form = UserAvatarUploadForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            img_obj = form.instance
            context = {"form": form, "img_obj": img_obj}
            return render(request, self.template_name, context)

    def get(self, request):
        form = UserAvatarUploadForm()
        context = {"form": form, "title": "Upload Avatar"}
        return render(request, self.template_name, context)


class LoginView(View):
    template_name = "registration/login.html"

    def get(self, request):
        context = {"form": LoginForm, "title": "Login"}
        return render(request, self.template_name, context)

    @method_decorator(csrf_protect)
    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get("password")
            email = form.cleaned_data.get("email")
            user = email_authenticate(email=email, password=password)
            login(request, user)
            return redirect("home")
        context = {"form": form}
        return render(request, self.template_name, context)


def register_confirm(request, token):
    redis_key = settings.USER_CONFIRMATION_KEY.format(token=token)
    user_info = cache.get(redis_key) or {}

    if user_id := user_info.get("user_id"):
        profile = get_object_or_404(Profile, user_id=user_id)
        profile.is_active_email = True
        profile.save(update_fields=["is_active_email"])
        return redirect(to=reverse_lazy("users:profile"))
    else:
        return redirect(to=reverse_lazy("users:register"))
