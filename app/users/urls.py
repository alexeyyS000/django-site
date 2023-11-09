from django.urls import path, include
from . import views

app_name = "users"
urlpatterns = [
    path("registartion/", views.RegisterUser.as_view(), name="registartion"),
    path("login/", views.CustomLogin.as_view(), name="login"),
    path("", include("django.contrib.auth.urls")),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("upload/", views.ImageUpload.as_view(), name="load_image"),
]
