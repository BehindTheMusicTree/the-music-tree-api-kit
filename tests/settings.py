SECRET_KEY = "fixture-only-not-for-production"

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "the_music_tree_api_kit",
    "tests.fixture_app",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
