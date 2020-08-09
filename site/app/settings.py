from django.core.files.uploadedfile import SimpleUploadedFile


__all__ = ("SETTINGS_DEFAULTS",)


SETTINGS_DEFAULTS = {
    "AppSettings": {
        "id": 1,
        "name": "Default name",
        "file": SimpleUploadedFile("default-file.pdf", None),
    }
}
