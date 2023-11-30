from celery import shared_task
from django.core.mail import EmailMessage


@shared_task
def send_message(serialized_email):
    serialized_email.pop("extra_headers")
    EmailMessage(**serialized_email).send()
    # изза ошибки "Object of type EmailMessage is not JSON serializable"
    # приходится сериализовать обьект в словарь перед передачей в delay()
    # и потом десериализовать здесь "EmailMessage(**email)", перед этим удалив поле extra_headers так как send() без этого не проходит
    return 0
