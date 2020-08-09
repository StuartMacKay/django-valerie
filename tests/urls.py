"""
Basic URL Configuration.

This is the minimum viable set of patterns to allow the various
views in the app and the Django Admin to be tested.

"""
from django.contrib import admin
from django.urls import path


urlpatterns = [
    path("admin/", admin.site.urls),
]
