"""
Tests for the AppSettings model, a concrete sub-class of Settings.

"""
from django.core.cache import InvalidCacheBackendError, caches

import pytest

import valerie.settings as base_settings

from app import settings as app_settings
from app.models import AppSettings


pytestmark = pytest.mark.django_db


def get_database_entry() -> AppSettings:
    """Get the settings object from the database."""
    return AppSettings.objects.first()


def set_database_entry(**kwargs) -> None:
    """Add the settings object to the database but not the cache."""
    obj = AppSettings.objects.create(**AppSettings.get_defaults(**kwargs))
    obj.purge()


def get_cache_entry() -> AppSettings:
    """Get the settings from the cache, if it exists."""
    cache_key = AppSettings.get_cache_key()
    return caches[AppSettings.get_cache_name()].get(cache_key)


def set_cache_entry(**kwargs) -> None:
    """Add the settings object to the cache but not the database."""
    name = AppSettings.get_cache_name()
    key = AppSettings.get_cache_key()
    timeout = AppSettings.get_cache_timeout()
    obj = AppSettings(**kwargs)
    caches[name].set(key, obj, timeout)


def setup_function(function):  # noqa
    """Setup for each test.

    Notes:
        All settings objects are deleted from the database and the cache
        is cleared before the start of each test. Pytest-django clears
        the database the same way Django's TestCase does but we do the
        delete here to make the starting state for the tests clear.

    """
    AppSettings.objects.all().delete()
    caches[AppSettings.get_cache_name()].clear()


#
# Tests for the get_settings() class method.
#


def test_get_app_setting_local():
    """Verify get_setting() fetches the setting from the local settings.py."""
    setting = AppSettings.get_setting(AppSettings.CACHE_NAME)
    assert setting == base_settings.SETTINGS_CACHE_NAME


def test_site_setting_overrides_app_setting(settings):
    """Verify get_setting() returns the setting from Django settings if defined."""
    settings.SETTINGS_CACHE_NAME = "other"
    setting = AppSettings.get_setting(AppSettings.CACHE_NAME)
    assert setting == "other" != base_settings.SETTINGS_CACHE_NAME


def test_missing_setting_raises_error():
    """Ensure get_setting() raises an error is the setting is undefined."""
    with pytest.raises(AttributeError):
        AppSettings.get_setting("missing")


#
# Tests for the get_defaults() class method.
#


def test_app_settings_defaults():
    """Verify get_defaults() returns the default field value from the local settings.py"""
    assert AppSettings.get_defaults() == app_settings.SETTINGS_DEFAULTS["AppSettings"]


def test_get_defaults_returns_app():
    """Verify that get_defaults() returns values for all the model fields."""
    defaults = AppSettings.get_defaults()
    for field in AppSettings._meta.fields:
        assert field.name in defaults


def test_get_defaults_creates_copy():
    """Verify get_defaults() returns a copy of the default settings."""
    AppSettings.get_defaults()["added"] = "value"
    assert "added" not in AppSettings.get_defaults()


def test_defaults_overridden_by_site_settings(settings):
    """Verify the Django settings override the values from the app's settings.py."""
    settings.SETTINGS_DEFAULTS = {"AppSettings": {"name": "Site name"}}
    defaults = AppSettings.get_defaults()
    assert defaults["name"] == "Site name"


def test_defaults_kwargs_overrides_site_settings(settings):
    """Verify values passed as kwargs to get_defaults() have highest priority."""
    settings.NAME = "Site name"
    defaults = AppSettings.get_defaults(name="kwarg name")
    assert defaults["name"] == "kwarg name"


#
# Tests for get_pk() class method.
#


def test_get_pk_default():
    """Verify get_pk() returns the values from the defaults."""
    assert app_settings.SETTINGS_DEFAULTS["AppSettings"]["id"] == AppSettings.get_pk()


def test_get_pk_missing():
    """Verify get_pk() return the default value on the class if not in the defaults"""
    value = app_settings.SETTINGS_DEFAULTS["AppSettings"]["id"]
    del app_settings.SETTINGS_DEFAULTS["AppSettings"]["id"]
    assert AppSettings.get_pk() == AppSettings.DEFAULT_PK
    app_settings.SETTINGS_DEFAULTS["AppSettings"]["id"] = value


#
# Tests for the get_cache() and get_cache_entry() class methods.
#


def test_get_cache_returns_cache():
    """Verify get_cache() returns the cache for settings."""
    assert "default" == AppSettings.get_cache_name()
    assert caches["default"] == AppSettings.get_cache()


def test_none_returned_if_caching_disabled(settings):
    """Verify setting SETTINGS_CACHE_NAME to None disables caching."""
    settings.SETTINGS_CACHE_NAME = None
    assert AppSettings.get_cache() is None


def test_none_returned_if_caching_undefined(settings):
    """Verify an error is raised if the wrong cache name is used."""
    with pytest.raises(InvalidCacheBackendError):
        settings.SETTINGS_CACHE_NAME = "other"
        assert AppSettings.get_cache() is None


def test_get_entry_from_cache():
    """Verify get_cache_entry() returns settings object from cache."""
    set_cache_entry(**AppSettings.get_defaults())
    assert AppSettings.get_cache_entry() is not None


def test_get_entry_from_cache_with_cache_disabled(settings):
    """Verify get_cache_entry() returns None if cache is disabled."""
    set_cache_entry(**AppSettings.get_defaults())
    settings.SETTINGS_CACHE_NAME = None
    assert AppSettings.get_cache_entry() is None


#
# Tests for the create() class method.
#


def test_create_saves_instance():
    """Verify create() adds the object to the database."""
    AppSettings.create()
    assert get_database_entry() is not None


def test_create_caches_instance():
    """Verify create() adds the object to the cache."""
    AppSettings.create()
    assert get_cache_entry() is not None


def test_create_overwrites_instance():
    """Calling create() multiple times overwrites existing instance."""
    AppSettings.create()
    AppSettings.create(name="updated")
    assert AppSettings.objects.count() == 1
    assert get_database_entry().name == "updated"


def test_create_with_cache_disabled(settings):
    """Verify create() skips updating the cache."""
    cache_name = AppSettings.get_cache_name()
    settings.SETTINGS_CACHE_NAME = None
    AppSettings.create()
    settings.SETTINGS_CACHE_NAME = cache_name
    assert get_cache_entry() is None


#
# Tests for the fetch() class method.
#


def test_fetch_with_cache_hit(django_assert_num_queries):
    """The settings object is fetched from the cache, if enabled."""
    set_database_entry(name="fetched from database")
    set_cache_entry(name="fetched from cache")
    with django_assert_num_queries(0):
        config = AppSettings.fetch()
    assert config.name == "fetched from cache"


def test_fetch_with_cache_miss(django_assert_num_queries):
    """The settings object is fetched from the database on cache miss."""
    set_database_entry(name="fetched from database")
    with django_assert_num_queries(1):
        obj = AppSettings.fetch()
    assert obj.name == "fetched from database"


def test_fetch_with_cache_disabled(settings, django_assert_num_queries):
    """The settings object is fetched from the database if the cache is disabled."""
    set_database_entry(name="fetched from database")
    set_cache_entry(name="fetched from cache")
    settings.SETTINGS_CACHE_NAME = None
    with django_assert_num_queries(1):
        obj = AppSettings.fetch()
    assert obj.name == "fetched from database"


def test_fetch_creates_object(django_assert_num_queries):
    """On a cache and database miss fetch() creates the settings object."""
    with django_assert_num_queries(3):
        obj = AppSettings.fetch()
    assert obj.name == AppSettings.get_defaults()["name"]
    assert get_cache_entry() is not None


#
# Tests for the model related save() and delete() methods.
#


def test_save_sets_primary_key():
    """Even if the primary key is overridden it is set when the settings are saved."""
    obj = AppSettings.create(id=2)
    assert obj.id == obj.get_pk() != 2


def test_save_adds_to_cache():
    """The save() adds the object to the cache."""
    AppSettings.create()
    assert get_cache_entry() is not None


def test_save_updates_cache():
    """The save() overwrites any existing entry in the cache."""
    set_cache_entry(name="overwrite me")
    AppSettings.create(name="overwritten")
    assert get_cache_entry().name == "overwritten"


def test_delete_from_database():
    """The delete() method deletes the object from the database."""
    obj = AppSettings.create()
    obj.delete()
    assert AppSettings.objects.count() == 0


def test_delete_from_cache():
    """The delete() method purges the object from the cache."""
    obj = AppSettings.fetch()
    obj.delete()
    assert get_cache_entry() is None


#
# Tests for the cache related cache() and purge() methods.
#


def test_cache_updates_cache():
    """Verify cache() adds an object to the cache."""
    obj = AppSettings(**AppSettings.get_defaults())
    obj.cache()
    assert get_cache_entry() is not None


def test_cache_with_cache_disabled(settings):
    """Verify cache() has no effect if cache is disabled."""
    obj = AppSettings(**AppSettings.get_defaults())
    cache_name = AppSettings.get_cache_name()
    settings.SETTINGS_CACHE_NAME = None
    obj.cache()
    settings.SETTINGS_CACHE_NAME = cache_name
    assert get_cache_entry() is None


def test_purge_clears_cache():
    """Verify purge() deletes the entry from the cache."""
    AppSettings.create().purge()
    assert get_cache_entry() is None


def test_purge_with_cache_disabled(settings):
    """Verify purge() has no effect if cache is disabled."""
    obj = AppSettings.create()
    cache_name = AppSettings.get_cache_name()
    settings.SETTINGS_CACHE_NAME = None
    obj.purge()
    settings.SETTINGS_CACHE_NAME = cache_name
    assert get_cache_entry() is not None
