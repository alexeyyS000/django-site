import datetime

from django.urls import reverse
from django.utils.safestring import mark_safe


def time_to_timedelta(time):
    return datetime.timedelta(hours=time.hour, minutes=time.minute, seconds=time.second, microseconds=time.microsecond)


def is_time_up(time_start, time_for_complete):
    time_left = time_for_complete - (datetime.datetime.now().replace(tzinfo=None) - time_start.replace(tzinfo=None))
    if time_left < datetime.timedelta(minutes=0, seconds=0):
        raise TimeoutError
    else:
        return time_left


def chop_microseconds(delta):
    return delta - datetime.timedelta(microseconds=delta.microseconds)


class EditLinkToInlineObjectMixin(object):
    def edit_link(self, instance):
        url = reverse("admin:%s_%s_change" % (instance._meta.app_label, instance._meta.model_name), args=[instance.pk])
        if instance.pk:
            return mark_safe('<a href="{u}">edit</a>'.format(u=url))
        else:
            return ""
