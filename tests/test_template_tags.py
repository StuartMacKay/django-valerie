"""
Tests for the valerie_settings template tag.

Notes:
    The tests here are mainly to verify the tag fails in specific ways
    if the path to the settings class is incorrect.

"""
from django.template import Context, Template

import pytest

from app.models import AppSettings


pytestmark = pytest.mark.django_db


def test_invalid_app_name():
    """When loading settings, an error is raised if the app name is incorrect."""
    template = Template(
        """
        {% load valerie_tags %}
        {% valerie_settings "ap.AppSettings" as settings  %}
        """
    )
    with pytest.raises(LookupError):
        template.render(Context())


def test_invalid_model_name():
    """When loading settings, an error is raised if the model name is incorrect."""
    template = Template(
        """
        {% load valerie_tags %}
        {% valerie_settings "app.ApSettings" as settings  %}
        """
    )
    with pytest.raises(LookupError):
        template.render(Context())


def test_missing_app_name():
    """When loading settings, an error is raised if the app name is not given."""
    template = Template(
        """
        {% load valerie_tags %}
        {% valerie_settings "AppSettings" as settings  %}
        """
    )
    with pytest.raises(ValueError):
        template.render(Context())


def test_missing_model_name():
    """When loading settings, an error is raised if the model name is not given."""
    template = Template(
        """
        {% load valerie_tags %}
        {% valerie_settings "app" as settings  %}
        """
    )
    with pytest.raises(ValueError):
        template.render(Context())


def test_module_name():
    """When loading settings, an error is raised if the module path is given."""
    template = Template(
        """
        {% load valerie_tags %}
        {% valerie_settings "app.models.AppSettings" as settings  %}
        """
    )
    with pytest.raises(ValueError):
        template.render(Context())


def test_load_settings():
    """The valerie_settings template tag loads the correct settings."""
    template = Template(
        """
        {% load valerie_tags %}
        {% valerie_settings "app.AppSettings" as settings  %}
        {{ settings.name }}
        {{ settings.file.url }}
        """
    )
    obj = AppSettings.fetch()
    output = template.render(Context())
    assert obj.name in output
    assert obj.file.url in output
