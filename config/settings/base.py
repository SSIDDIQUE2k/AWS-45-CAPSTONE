import os
import subprocess
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent


def get_env(key, default=""):
    val = os.environ.get(key)
    if val:
        return val
    try:
        out = subprocess.check_output(["cat", ".env"]).decode()
        for line in out.splitlines():
            if line.startswith(f"{key}="):
                return line.split("=", 1)[1].strip()
    except Exception:
        pass
    print(f"[WARN] {key} not set. Using default/dummy value.")
    return default


SECRET_KEY = get_env("DJANGO_SECRET_KEY", "dev-secret-key")
DEBUG = get_env("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = get_env("DJANGO_ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'channels',
    'storages',
    'pgvector.django',
    'agent',
    'kb',
    'chat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'


# Database
DB_NAME = get_env('POSTGRES_DB', 'finguide')
DB_USER = get_env('POSTGRES_USER', 'postgres')
DB_PASSWORD = get_env('POSTGRES_PASSWORD', 'postgres')
DB_HOST = get_env('POSTGRES_HOST', 'localhost')
DB_PORT = get_env('POSTGRES_PORT', '5432')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    }
}


# Redis / Celery
REDIS_URL = get_env('REDIS_URL', 'redis://localhost:6379/0')
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL


# Storage
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

AWS_S3_ENDPOINT_URL = get_env('S3_ENDPOINT_URL', '')
AWS_ACCESS_KEY_ID = get_env('S3_ACCESS_KEY', '')
AWS_SECRET_ACCESS_KEY = get_env('S3_SECRET_KEY', '')
AWS_STORAGE_BUCKET_NAME = get_env('S3_BUCKET', '')


# Static/Media
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
STATICFILES_DIRS = [BASE_DIR / 'static']


# DRF
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}


# Channels
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
        },
    },
}


# Vector / Embeddings
EMBEDDING_MODEL_NAME = get_env('EMBEDDING_MODEL_NAME', 'intfloat/e5-small-v2')
RERANKER_MODEL_NAME = get_env('RERANKER_MODEL_NAME', 'BAAI/bge-reranker-large')


# Hugging Face Inference (OpenAI-compatible)
HF_API_URL = get_env('HF_API_URL', 'https://example-hf-endpoint/v1')
HF_API_KEY = get_env('HF_API_KEY', 'dummy-key')
HF_MODEL = get_env('HF_MODEL', 'meta-llama/Meta-Llama-3-8B-Instruct')


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
