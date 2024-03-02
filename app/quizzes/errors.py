from http import HTTPStatus

from django.utils.translation import gettext_lazy as _

from app.utils.errors import BaseHttpError


class PageNotFoundError(BaseHttpError):
    status = HTTPStatus.NOT_FOUND
    error_name = "Page not found."
    message = "The page you’re looking for doesn’t exist."


class TestNotFoundError(BaseHttpError):
    status = HTTPStatus.NOT_FOUND
    error_name = "Test not found."
    message = "The test you’re looking for doesn’t exist."


class AttemptNotFoundError(BaseHttpError):
    status = HTTPStatus.NOT_FOUND
    error_name = "Attempt not found."
    message = "The attempt you’re looking for doesn’t exist."


class QuestionNotFoundError(BaseHttpError):
    status = HTTPStatus.NOT_FOUND
    error_name = "Question not found."
    message = "The Question you’re looking for doesn’t exist."


class BadRequestParametrError(BaseHttpError):
    status = HTTPStatus.BAD_REQUEST
    error_name = "Bad request."
    message = "You are sending an invalid parameter."
