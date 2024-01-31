from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.utils.translation import gettext_lazy as _


@shared_task
def send_message(
    from_email: str = None, subject: str = None, body: str = None, html_email: str = None, *args: str
) -> int:
    email_message = EmailMultiAlternatives(subject, body, from_email, *args)
    if html_email is not None:
        email_message.attach_alternative(html_email, "text/html")
    email_message.send()
    return 0
