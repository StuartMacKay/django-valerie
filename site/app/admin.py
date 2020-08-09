from django.contrib import admin

from valerie.admin import SettingsAdmin

from .models import AppSettings


@admin.register(AppSettings)
class AppSettingsAdmin(SettingsAdmin):
    pass
