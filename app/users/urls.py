from django.urls import include
from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
    path("signup/", views.RegisterUserView.as_view(), name="signup"),
    path("login/", views.LoginView.as_view(), name="login"),
    path(
        "reset/<uidb64>/<token>/",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("password_reset/", views.PasswordResetView.as_view(), name="password_reset"),
    path("", include("django.contrib.auth.urls")),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("upload/", views.ImageUploadView.as_view(), name="load_image"),
    path("register_confirm/<token>/", views.register_confirm, name="register_confirm"),
]
