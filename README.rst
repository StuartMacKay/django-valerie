==============
Django Valerie
==============

A Django app that provides a singleton model so you can store your settings
in the database.

Supports Python 3.6-3.8 or later and Django 2.2-3.1.


Quickstart
==========

Install the app using pip::

    pip install django-valerie

Add it to your installed apps::

    INSTALLED_APPS = [
      ...
      'valerie',
    ]

Create a model for your settings, for example::

    # models.py
    from django.db import models

    from valerie.models import Settings


    class MySettings(Settings):

        site = models.CharField(max_length=50)
        logo = models.FileField(upload_to="files")
        comments = models.BooleanField()

Create settings.py next to the model and add the default values for each
field::

    from django.core.files.uploadedfile import SimpleUploadedFile


    SETTINGS_DEFAULTS = {
        "MySettings": {
            "id": 1,
            "site": "My Awesome Site",
            "logo": SimpleUploadedFile("logo.png", None),
            "comments": True,
        }
    }

Now register the settings with the Django Admin::

    from django.contrib import admin

    from valerie.admin import SettingsAdmin

    from .models import MySettings


    @admin.register(MySettings)
    class MySettingsAdmin(SettingsAdmin):
        pass

The record is added, using the defaults, to the database on demand so
you can immediately use the settings in your code without needing to
do any migrations::

    settings = MySettings.fetch()

Or in a template by giving the `<app>.<model>` path::

    {% load valerie_tags %}

    {% valerie_settings "myapp.MySettings" as settings %}

You can now turn over control to your site admin staff to update the values.

Caching
=======
If you have caching enabled there are three settings which control whether
and where the settings object is cached and for how long:::

    SETTINGS_CACHE_NAME = 'default'

    SETTINGS_CACHE_TIMEOUT = 60 * 60  # 1 hour

    SETTINGS_CACHE_PREFIX = "settings"

The default stores the settings in the `default` cache for 1 hour (which seems
reasonable given they should change relatively slowly).

The cache is refreshed whenever a settings object is accessed and the cache
entry had expired. The cache is also updated every time a settings object is
saved.

The settings are stored in `valerie.settings` so the app has sensible defaults.
You can override some or all of these in the Django settings.

Sensible defaults
=================
The default values for each required field in your settings model are defined
in setting `SETTINGS_DEFAULTS` which is a dictionary with entries for each
`Settings` class in and apps' models::

    SETTINGS_DEFAULTS = {
        "MySettings": {
            "id": 1,
            "site": "My Awesome Site",
            "logo": SimpleUploadedFile("logo.png", None),
            "comments": True,
        }
    }

As with the cache settings any `Settings` subclass loads the values from
`settings.py` in the same app then checks the (main) Django settings for any
overrides. That make it easy to use `django-valerie` in an app you distribute
as your sensible defaults can be overridden as needed.

Demo site
=========
If you check out the code from the repository, the project contains a demo
site with an example app that contains concrete subclass of the `Settings`
class so you can see how django-valerie works.

Make it so
==========
The project has a ``Makefile`` that contains a number of targets to support the
development process. The most useful are probably `tests` for running the tests
and `runserver` for running the demo site to show the Django Admin site. There
is also a set of targets to manage the release process.

You can read a brief description by running ``make`` on the command line::

    make


Similar to
==========

* `django-solo`_

.. _django-solo: https://github.com/lazybird/django-solo
