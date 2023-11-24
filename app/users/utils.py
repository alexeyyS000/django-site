from django.contrib.auth import get_user_model
from django_countries import countries

UserModel = get_user_model()


def email_authenticate(email=None, password=None):
    try:
        user = UserModel.objects.get(email=email)
    except UserModel.DoesNotExist:
        return None
    else:
        if user.check_password(password):
            return user
    return None


def fill_county_table(apps, schema_editor):
    Country = apps.get_model("users", "Country")
    for country in countries:
        Country.objects.create(country=country)
