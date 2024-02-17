from django.db.models import Model


def get_one_or_none(classmodel: Model, **kwargs: dict):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None
