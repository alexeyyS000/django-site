from http import HTTPStatus

from django.conf import settings
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from .utils.errors import BaseHttpError


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
            return HttpResponse("Error processing the request.", status=HTTPStatus.INTERNAL_SERVER_ERROR)


class LanguageMiddleware:
    def __init__(self, get_response: HttpResponse):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        cookie_lang = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
        if cookie_lang:
            translation.activate(cookie_lang)
            response = self.get_response(request)
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, cookie_lang)
        else:
            response = self.get_response(request)

        return response
