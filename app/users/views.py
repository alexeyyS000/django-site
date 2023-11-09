from django.shortcuts import render, redirect
from users.forms import UserCreationForm, CustomLoginform
from django.views import View
from django.contrib.auth import authenticate, login
from .forms import ImageLoad
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin

class RegisterUser(View):
    template_name = "registration/register.html"

    def get(self, request):
        context = {"form": UserCreationForm}
        return render(request, self.template_name, context)

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            password = form.cleaned_data.get("password1")
            email = form.cleaned_data.get("email")
            user = authenticate(email=email, password=password)
            login(request, user)
            return redirect("home")
        context = {"form": form}
        return render(request, self.template_name, context)


class ProfileView(LoginRequiredMixin, View):
    template_name = "profile.html"

    def get(self, request):
        if request.method == "GET":
            context = {"form": AuthenticationForm}
            return render(request, self.template_name, context)


class ImageUpload(LoginRequiredMixin, View):
    template_name = "imgload.html"

    def post(self, request):
        form = ImageLoad(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            img_obj = form.instance
            context = {"form": form, "img_obj": img_obj}
            return render(request, self.template_name, context)

    def get(self, request):
        form = ImageLoad()
        context = {"form": form}
        return render(request, self.template_name, context)


class CustomLogin(View):
    template_name = "registration/login.html"

    def get(self, request):
        context = {"form": CustomLoginform}
        return render(request, self.template_name, context)

    @method_decorator(csrf_protect)
    def post(self, request):
        form = CustomLoginform(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get("password")
            email = form.cleaned_data.get("email")
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
            else:
                form.full_clean()
                return render(request, self.template_name, {"form": form})
            return redirect("home")
        context = {"form": form}
        return render(request, self.template_name, context)
