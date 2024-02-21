import datetime

from ..errors import BadRequestParametrError



def is_time_up(time_start:datetime.datetime, time_for_complete:datetime.timedelta):
    time_left = time_for_complete - (datetime.datetime.now().replace(tzinfo=None) - time_start.replace(tzinfo=None))
    if time_left < datetime.timedelta(minutes=0, seconds=0):
        raise TimeoutError
    else:
        return time_left


def chop_microseconds(delta:datetime.timedelta):
    return delta - datetime.timedelta(microseconds=delta.microseconds)


def check_validity_request_ints(*args:str):
    for i in args:
        try:
            int(i)
        except ValueError:
            raise BadRequestParametrError
