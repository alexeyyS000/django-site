from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect

from .forms import LoginForm
from .forms import UserAvatarUploadForm
from .forms import UserCreationForm
from .models import User
from .tasks import send_message
from .utils import email_authenticate
from .utils import generate_confirm_email
from .utils import set_cache


class RegisterUserView(View):
    template_name = "registration/register.html"

    def get(self, request):
        context = {"form": UserCreationForm}
        return render(request, self.template_name, context)

    @method_decorator(csrf_protect)
    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            password = form.cleaned_data.get("password1")
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            user = authenticate(username=username, password=password)
            token = set_cache(
                settings.USER_CONFIRMATION_TIMEOUT, settings.USER_CONFIRMATION_KEY, **{"user_id": user.id}
            )
            email = generate_confirm_email(request, token, email)
            serialized_email = email.__dict__
            send_message.delay(serialized_email)
            login(request, user)
            return redirect("home")
        context = {"form": form}
        return render(request, self.template_name, context)


class ProfileView(LoginRequiredMixin, View):
    template_name = "profile.html"

    def get(self, request):
        context = {"form": AuthenticationForm}
        return render(request, self.template_name, context)


class ImageUploadView(LoginRequiredMixin, View):
    template_name = "imgload.html"

    def post(self, request):
        form = UserAvatarUploadForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            img_obj = form.instance
            context = {"form": form, "img_obj": img_obj}
            return render(request, self.template_name, context)

    def get(self, request):
        form = UserAvatarUploadForm()
        context = {"form": form}
        return render(request, self.template_name, context)


class LoginView(View):
    template_name = "registration/login.html"

    def get(self, request):
        context = {"form": LoginForm}
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
        user = get_object_or_404(User, id=user_id)
        user.is_active_email = True
        user.save(update_fields=["is_active_email"])
        return redirect(to=reverse_lazy("users:profile"))
    else:
        return redirect(to=reverse_lazy("users:signup"))
