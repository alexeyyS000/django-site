from django.utils.translation import gettext_lazy as _
from app.utils.errors import BaseHttpError


class PageNotFoundError(BaseHttpError):
    status = 404
    error_name = "Page not found."
    message = "The page you’re looking for doesn’t exist."


class TestNotFoundError(BaseHttpError):
    status = 404
    error_name = "Test not found."
    message = "The test you’re looking for doesn’t exist."


class BadRequestParametrError(BaseHttpError):
    status = 400
    error_name = "Bad request."
    message = "You are sending an invalid parameter."
