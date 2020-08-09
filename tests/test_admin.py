"""
Tests to verify the various views in the Django Admin can be displayed
for the Config model.

Notes:
    These are mainly smoke tests to see if the page renders without any
    errors.

    The fixture is used to create the Config object in the database. We
    don't want the cache involved since it would need to be cleared for
    every test.

TODO:
    * Add test for breadcrumbs to verify only the class name is shown and
      the instance id is not.

"""
from django.urls import reverse

import pytest

from app.models import AppSettings


pytestmark = pytest.mark.django_db


@pytest.fixture
def app_settings():
    return AppSettings.objects.create(**AppSettings.get_defaults())


def test_changelist_view(admin_client, app_settings):
    url = reverse("admin:app_appsettings_changelist")
    assert admin_client.get(url).status_code == 200


def test_change_view(admin_client, app_settings):
    url = reverse("admin:app_appsettings_change", args=(app_settings.pk,))
    assert admin_client.get(url).status_code == 200


def test_history_view(admin_client, app_settings):
    url = reverse("admin:app_appsettings_history", args=(app_settings.pk,))
    assert admin_client.get(url).status_code == 200
