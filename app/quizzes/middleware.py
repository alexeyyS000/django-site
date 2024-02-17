from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from .errors import BaseHttpError


class ErrorHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if not settings.DEBUG:
            if isinstance(exception, BaseHttpError):
                return render(
                    request,
                    "errors/base.html",
                    {"status": exception.status, "message": exception.message, "error_name": exception.error_name},
                )
            return HttpResponse("Error processing the request.", status=500)
