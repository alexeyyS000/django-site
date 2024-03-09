import datetime

from ..errors import BadRequestParametrError


def get_time_left(time_start: datetime.datetime, time_for_complete: datetime.timedelta):
    time_left = time_for_complete - (
        datetime.datetime.now().replace(tzinfo=None) - time_start.replace(tzinfo=None)
    )  # работать в utc
    return time_left


def chop_microseconds(delta: datetime.timedelta):
    if delta:
        return delta - datetime.timedelta(microseconds=delta.microseconds)
    else:
        return None


def check_validity_request_ints(*args: str):
    for i in args:
        try:
            int(i)
        except ValueError:
            raise BadRequestParametrError
