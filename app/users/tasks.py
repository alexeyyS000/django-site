from celery import shared_task
from django.core.mail import EmailMessage
from django.utils.translation import gettext_lazy as _


@shared_task
def send_confirm_message(confirm_link: str, email_adress: str) -> int:
    message = _(f"follow this link %s \n" f"to confirm! \n" % confirm_link)
    email = EmailMessage("please confirm your eamail", message, to=[email_adress])
    email.send()
    return 0
