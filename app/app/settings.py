"""
Django settings for app project.

Generated by 'django-admin startproject' using Django 4.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

from . import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!

# ALLOWED_HOSTS = []
ALLOWED_HOSTS = [f"{config.HOST}", "app"]

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "quizzes.apps.QuizzesConfig",
    "users.apps.UsersConfig",
    "minio_storage",
    "django_countries",
    "django_filters",
    "adminsortable2",
    "django_admin_search",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "app.middleware.ErrorHandlerMiddleware",
]

ROOT_URLCONF = "app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "app.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config.POSTGRES_DB,
        "USER": config.POSTGRES_USER,
        "PASSWORD": config.POSTGRES_PASSWORD,
        "HOST": config.DB_HOST,
        "PORT": "5432",
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

DEBUG = True


STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "statics"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


CSRF_TRUSTED_ORIGINS = [
    "https://nginx.your-domain.com",
    "https://www.nginx.your-domain.com",
    "http://nginx.your-domain.com",
    f"http://{config.HOST}:80",
]

DEFAULT_FILE_STORAGE = "minio_storage.storage.MinioMediaStorage"
MINIO_STORAGE_ENDPOINT = config.MINIO_STORAGE_ENDPOINT
MINIO_STORAGE_ACCESS_KEY = config.MINIO_STORAGE_ACCESS_KEY
MINIO_STORAGE_SECRET_KEY = config.MINIO_STORAGE_SECRET_KEY
MINIO_STORAGE_USE_HTTPS = False
MINIO_STORAGE_MEDIA_BUCKET_NAME = "local-media"
MINIO_STORAGE_MEDIA_BACKUP_BUCKET = "local-media"
MINIO_STORAGE_MEDIA_BACKUP_FORMAT = "%c/"
MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = True
MINIO_STORAGE_STATIC_BUCKET_NAME = "local-static"
MINIO_STORAGE_AUTO_CREATE_STATIC_BUCKET = True

if config.IS_DEV_MAIL == "True":
    EMAIL_HOST = "mailpit"
    EMAIL_PORT = 1025
    EMAIL_HOST_USER = ""
    EMAIL_HOST_PASSWORD = ""
    DEFAULT_FROM_EMAIL = "test@mail.com"
else:
    EMAIL_HOST = "smtp.yandex.ru"
    EMAIL_PORT = 465
    EMAIL_USE_TLS = False
    EMAIL_USE_SSL = True

    EMAIL_HOST_USER = config.EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD = config.EMAIL_HOST_PASSWORD
    DEFAULT_FROM_EMAIL = config.DEFAULT_FROM_EMAIL
    # EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
    }
}


USER_CONFIRMATION_KEY = "user_confirmation_{token}"
USER_CONFIRMATION_TIMEOUT = 300


CELERY_BROKER_URL = config.CELERY_BROKER_URL
CELERY_RESULT_BACKEND = config.CELERY_RESULT_BACKEND


MINIO_STORAGE_MEDIA_URL = f"http://{config.HOST}:80/media/local-media/"

AUTH_USER_MODEL = "users.User"
