"""
Model for cresting singletons for storing settings in the database.

Todo:
    * There are still a couple of inconsistencies between the way objects
      behave with the cache and the database. For example, you can delete
      an object from the database but still add it to the cache.
    * Should the cache key use the object's actual pk rather than the
      assumed value (the default from the settings or the DEFAULT_PK value.

"""
from importlib import import_module
from typing import Tuple, Type

from django.conf import settings as site_settings
from django.core.cache import caches
from django.db import models
from django.utils.translation import gettext_lazy as _


__all__ = ("Settings",)


class Settings(models.Model):
    """
    Base class for a settings singleton.

    To use, create a subclass add it to your models.py. Then create a
    settings.py in the same app/module and define SETTINGS_DEFAULTS which
    contains a dictionary values to initialise all the fields in your model.
    For example::

        SETTINGS_DEFAULTS = {
            "MySettings": {
                "id": 1,
                "title": "My Site",
                "comments": True,
                ...
            }
        }

    Each settings singleton will first load the defaults from it's local setting
    file and then checks Django's (global) settings for any values you want to
    override. That makes it possible to ship apps which have sensible defaults
    which then can be selectively overridden.

    """

    CACHE_NAME = "SETTINGS_CACHE_NAME"
    CACHE_TIMEOUT = "SETTINGS_CACHE_TIMEOUT"
    CACHE_PREFIX = "SETTINGS_CACHE_PREFIX"
    DEFAULTS = "SETTINGS_DEFAULTS"

    DEFAULT_PK = 1

    class Meta:
        abstract = True
        verbose_name = _("Settings")
        verbose_name_plural = _("Settings")

    @classmethod
    def get_setting(cls, name):
        app_settings = import_module("valerie.settings")
        return getattr(site_settings, name, getattr(app_settings, name))

    @classmethod
    def get_app_settings(cls):
        return import_module("..settings", package=cls.__module__)

    @classmethod
    def get_app_setting(cls, name):
        return getattr(cls.get_app_settings(), name)

    @classmethod
    def get_defaults(cls, **kwargs) -> dict:
        """
        Get the default values for each field in the model.

        """
        app_defaults = cls.get_app_setting(cls.DEFAULTS)
        site_defaults = getattr(site_settings, cls.DEFAULTS, {})
        defaults = app_defaults.get(cls.__name__, {}).copy()
        defaults.update(site_defaults.get(cls.__name__, {}))
        defaults.update(kwargs)
        return defaults

    @classmethod
    def get_pk(cls) -> int:
        return cls.get_defaults().get("id", cls.DEFAULT_PK)

    @classmethod
    def get_cache_name(cls) -> str:
        return cls.get_setting(cls.CACHE_NAME)

    @classmethod
    def get_cache_timeout(cls) -> int:
        return cls.get_setting(cls.CACHE_TIMEOUT)

    @classmethod
    def get_cache_prefix(cls) -> str:
        return cls.get_setting(cls.CACHE_PREFIX)

    @classmethod
    def get_cache_key(cls) -> str:
        return "%s:%s:%d" % (cls.get_cache_prefix(), cls.__name__.lower(), cls.get_pk())

    @classmethod
    def get_cache(cls):
        name = cls.get_cache_name()
        return caches[name] if name else None

    @classmethod
    def get_cache_entry(cls) -> (Type["Settings"], None):
        """Get the settings object from the cache."""
        cache = cls.get_cache()
        return cache.get(cls.get_cache_key()) if cache else None

    @classmethod
    def create(cls, **kwargs):
        """
        Create/re-generate the settings object from the defaults.

        """
        obj = cls(**cls.get_defaults(**kwargs))
        obj.save()
        return obj

    @classmethod
    def fetch(cls):
        """
        Fetch the settings singleton returning it from the cache, if enabled,
        otherwise the database.

        """
        obj = cls.get_cache_entry()
        if obj is None:  # cache miss
            obj = cls.objects.first()
            if obj is None:  # database miss
                obj = cls.create()
            else:
                obj.cache()
        return obj

    def __str__(self) -> str:
        return "%s" % self._meta.verbose_name

    def save(self, *args, **kwargs) -> None:
        """
        Save the settings to the database and update the cache, if enabled.

        Notes:
            The primary key is set explicitly to prevent multiple instances
            from being created. This could happen with modelform_factory in
            the Django Admin since it ignores any primary key value defined
            in the defaults.

            Since this is an abstract class it's much easier to simply override
            save() rather than use the pre_save signal.

        """
        self.pk = self.get_pk()
        super(Settings, self).save(*args, **kwargs)
        self.cache()

    def delete(self, *args, **kwargs) -> Tuple[int, dict]:
        """Delete the object from the database and the cache, if enabled."""
        self.purge()
        return super(Settings, self).delete(*args, **kwargs)

    def cache(self) -> None:
        """Add the object to the cache, if enabled."""
        cache = self.get_cache()
        if cache:
            key = self.get_cache_key()
            timeout = self.get_cache_timeout()
            cache.set(key, self, timeout)

    def purge(self) -> None:
        """Delete the object from the cache, if enabled."""
        cache = self.get_cache()
        if cache:
            # Fails silently if the object does not exist.
            cache.delete(self.get_cache_key())
