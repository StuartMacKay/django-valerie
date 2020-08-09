# The name of the cache where the settings will be stored. Caching is
# disables if this setting is None.
SETTINGS_CACHE_NAME = "default"

# The time in seconds that the setting will be cached for.
SETTINGS_CACHE_TIMEOUT = 60 * 60  # 1 hour

# A prefix that is added to the cache key to avoid the chance of collisions.
# This is in addition to any value defined in the KEY_PREFIX setting.
SETTINGS_CACHE_PREFIX = "settings"

# The dictionary containing the defaults for each field in a settings class.
# Each key is the class name and the value is a dict with key and values for
# each field in the model that needs a default value.
#
# Since Settings is an abstract class these defaults will never be used. The
# settings defined local to the concrete subclass will be loaded. A default
# value is define here as an example:
#
# SETTINGS_DEFAULTS = {
#   "Settings": {
#     "id": 1,
#     "site": "My Awesome Site",
#     "logo": SimpleUploadedFile("logo.png", None),
#     "comments": True,
#     ...
#   }
# }


__all__ = (
    "SETTINGS_CACHE_NAME",
    "SETTINGS_CACHE_TIMEOUT",
    "SETTINGS_CACHE_PREFIX",
)
