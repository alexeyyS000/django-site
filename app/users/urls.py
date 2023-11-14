from django.urls import include
from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
    path("registartion/", views.RegisterUserView.as_view(), name="registartion"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("", include("django.contrib.auth.urls")),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("upload/", views.ImageUploadView.as_view(), name="load_image"),
]
