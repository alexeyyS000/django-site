import uuid

from django.core.cache import cache
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


def generate_confirm_link(request, token) -> str:
    confirm_link = request.build_absolute_uri(reverse_lazy("users:register_confirm", kwargs={"token": token}))
    return confirm_link


def set_verification_token(token, timeout: int, temlpale: str, **kwargs):
    redis_key = temlpale.format(token=token)
    set_cache = cache.set(redis_key, kwargs, timeout=timeout)
    return set_cache


def get_cache(redis_key):
    get_cache = cache.get(redis_key) or {}
    return get_cache


def generate_token():
    return uuid.uuid4().hex
