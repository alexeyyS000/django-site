from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect

from .forms import ImageLoadForm
from .forms import LoginForm
from .forms import UserCreationForm
from .utils import email_authenticate


class RegisterUserView(View):
    template_name = "registration/register.html"

    def get(self, request):
        context = {"form": UserCreationForm}
        return render(request, self.template_name, context)

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            password = form.cleaned_data.get("password1")
            username = form.cleaned_data.get("username")
            form.save()
            user = authenticate(username=username, password=password)
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
        form = ImageLoadForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            img_obj = form.instance
            context = {"form": form, "img_obj": img_obj}
            return render(request, self.template_name, context)

    def get(self, request):
        form = ImageLoadForm()
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
            if user is not None:
                login(request, user)
            else:
                return render(request, self.template_name, {"form": form})
            return redirect("home")
        context = {"form": form}
        return render(request, self.template_name, context)
