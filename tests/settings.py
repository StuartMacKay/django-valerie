"""
MVS (Minimalist Viable Settings) for running tests.

"""
import os
import sys


DEBUG = True

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(TESTS_DIR)

# Add the src directory to the PYTHONPATH
sys.path.append(os.path.join(PROJECT_DIR, "src"))
# Use the concrete Settings class, AppSettings, from the site app in the tests
sys.path.append(os.path.join(PROJECT_DIR, "site"))

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "valerie.apps.ValerieAppConfig",
    "app",
)

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]

ROOT_URLCONF = "tests.urls"

STATIC_URL = "/static/"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(PROJECT_DIR, "db.sqlite3"),
    }
}
