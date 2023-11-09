from django.urls import path, include
from . import views
from django.contrib.auth.decorators import login_required

app_name = "users"
urlpatterns = [
    path("registartion/", views.RegisterUser.as_view(), name="registartion"),
    path("login/", views.CustomLogin.as_view(), name="login"),
    path("", include("django.contrib.auth.urls")),
    path("profile/", login_required(views.ProfileView.as_view()), name="profile"),
    path("upload/", login_required(views.ImageUpload.as_view()), name="load_image"),
]
