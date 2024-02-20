from django.utils.translation import gettext_lazy as _
from .utils.exceptions import BaseHttpError


class PageNotFoundError(BaseHttpError):
    status = 404
    error_name = "Page not found."
    message = "The page you’re looking for doesn’t exist."


class TestNotFoundError(BaseHttpError):
    status = 404
    error_name = "Test not found."
    message = "The test you’re looking for doesn’t exist."


class BadFindParametrError(BaseHttpError):
    status = 400
    error_name = "Bad find request."
    message = "You are sending an invalid find parameter."
