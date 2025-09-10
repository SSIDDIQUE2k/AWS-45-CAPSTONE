from .base import *  # noqa

# Local overrides (kept minimal)
DEBUG = True

# Override database to use SQLite for development without pgvector issues
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Remove pgvector from installed apps for SQLite compatibility
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'pgvector.django']

