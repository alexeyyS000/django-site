import uuid

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

UserModel = get_user_model()


def email_authenticate(email: str, password: str):
    try:
        user = UserModel.objects.get(email=email)
    except UserModel.DoesNotExist:
        return None
    else:
        if user.check_password(password):
            return user
    return None


def generate_confirm_email(request, token, email: str):
    confirm_link = request.build_absolute_uri(reverse_lazy("users:register_confirm", kwargs={"token": token}))
    message = _(f"follow this link %s \n" f"to confirm! \n" % confirm_link)
    email = EmailMessage("please confirm your eamail", message, to=[email])
    return email


def set_cache(timeout: int, temlpale: str, **kwargs):
    token = uuid.uuid4().hex
    redis_key = temlpale.format(token=token)
    cache.set(redis_key, kwargs, timeout=timeout)
    return token
