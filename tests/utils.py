import django
from django.conf import settings

from . import settings as test_settings


def get_test_settings(**kwargs):
    values = {k: getattr(test_settings, k) for k in dir(test_settings) if k.isupper()}
    values.update(kwargs)
    return values


def configure_django(**kwargs):
    local_settings = get_test_settings(**kwargs)
    settings.configure(**local_settings)
    django.setup()
