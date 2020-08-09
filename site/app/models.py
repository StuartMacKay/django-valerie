from django.db import models

from valerie.models import Settings


class AppSettings(Settings):

    name = models.CharField(max_length=50)
    file = models.FileField(upload_to="files")
