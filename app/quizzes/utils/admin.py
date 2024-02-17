from django.urls import reverse
from django.utils.safestring import mark_safe


class EditLinkToInlineObjectMixin(object):
    def link(self, instance):
        url = reverse("admin:%s_%s_change" % (instance._meta.app_label, instance._meta.model_name), args=[instance.pk])
        if instance.pk:
            return mark_safe('<a href="{u}">edit</a>'.format(u=url))
        else:
            return ""
