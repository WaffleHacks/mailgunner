"""
Django settings for mailgunner project.

Generated by 'django-admin startproject' using Django 3.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from django.contrib.messages import constants as messages
import dj_database_url
from dotenv import load_dotenv
from json import loads as parse_json
from os import environ
from pathlib import Path
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Load .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = environ.get("DEBUG", "no") == "yes"

ALLOWED_HOSTS = ["127.0.0.1", "localhost", environ.get("PUBLIC_URL")]

# Secure cookies
HTTPS = environ.get("HTTPS", "no") == "yes"
CSRF_COOKIE_SECURE = HTTPS
SESSION_COOKIE_SECURE = HTTPS

# HSTS configuration
#   enable for 6 months
#   preload certificates
#   include subdomains in HSTS
SECURE_HSTS_SECONDS = 15778800 if HTTPS else None
SECURE_HSTS_PRELOAD = HTTPS
SECURE_HSTS_INCLUDE_SUBDOMAINS = HTTPS

# Redirect HTTP to HTTPS
SECURE_SSL_REDIRECT = HTTPS
if HTTPS:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# Application definition

INSTALLED_APPS = [
    "anymail",
    "whitenoise.runserver_nostatic",
    "account.apps.AuthenticationConfig",
    "conversations.apps.IncomingConfig",
    "schedule.apps.ScheduleConfig",
    "django_better_admin_arrayfield",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "mailgunner.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "mailgunner.wsgi.application"


# Default database configuration (for local development)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "172.17.0.3",
        "PORT": "5432",
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Load database config from environment
db_from_env = dj_database_url.config("DATABASE_URL", conn_max_age=600)
DATABASES["default"].update(db_from_env)


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 12,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Password hashers
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Vancouver"
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Mailer configuration
ANYMAIL = {
    "MAILGUN_API_KEY": environ.get("MAILGUN_API_KEY"),
    "MAILGUN_SENDER_DOMAIN": environ.get("MAILGUN_DOMAIN"),
    "MAILGUN_WEBHOOK_SIGNING_KEY": environ.get("MAILGUN_WEBHOOK_SIGNING_KEY"),
    "WEBHOOK_SECRET": environ.get("WEBHOOK_SECRET"),
}
EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
DEFAULT_FROM_EMAIL = "no-reply@" + environ.get("MAILGUN_DOMAIN", "")
SERVER_EMAIL = "mailgunner@" + environ.get("MAILGUN_DOMAIN", "")

# Login redirects
LOGIN_URL = "account:login"
LOGIN_REDIRECT_URL = "/"

# AWS S3 storage backend configuration
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_ACCESS_KEY_ID = environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = environ.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = environ.get("AWS_S3_REGION_NAME")

# Custom message levels to match with Bootstrap's colors
# Only debug and error need to be changed since the rest match with Bootstrap
MESSAGE_TAGS = {
    messages.DEBUG: "secondary",
    messages.ERROR: "danger",
}

# Celery configuration
CELERY_BROKER_URL = environ.get("REDIS_URL")
CELERY_RESULT_BACKEND = environ.get("REDIS_URL")
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]

# Authlib Discord provider configuration
DISCORD_GUILD_ID = environ.get("DISCORD_GUILD_ID")
AUTHLIB_OAUTH_CLIENTS = {
    "discord": {
        "client_id": environ.get("DISCORD_CLIENT_ID"),
        "client_secret": environ.get("DISCORD_CLIENT_SECRET"),
    }
}

# Integrate Sentry
SENTRY_DSN = environ.get("SENTRY_DSN")
sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.5,
    environment="development" if DEBUG else "production",
    send_default_pii=True,
)
