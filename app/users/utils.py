import uuid

from django.core.cache import cache
from django.http import HttpRequest
from django.urls import reverse_lazy

from .models import User


def email_authenticate(email: str, password: str) -> User | None:
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return None
    else:
        if user.check_password(password):
            return user
    return None


def generate_confirm_link(request: HttpRequest, token: str) -> str:
    confirm_link = request.build_absolute_uri(reverse_lazy("users:register_confirm", kwargs={"token": token}))
    return confirm_link


def set_verification_token(token: str, timeout: int, temlpale: str, **kwargs: str) -> bool:
    redis_key = temlpale.format(token=token)
    set_cache = cache.set(redis_key, kwargs, timeout=timeout)
    return set_cache


def get_cache(redis_key: str) -> dict:
    get_cache = cache.get(redis_key) or {}
    return get_cache


def generate_token() -> str:
    return uuid.uuid4().hex
