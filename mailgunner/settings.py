"""
Django settings for mailgunner project.

Generated by 'django-admin startproject' using Django 3.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import dj_database_url
from dotenv import load_dotenv
from os import environ
from pathlib import Path

# Load .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = environ.get('DEBUG', 'no') == 'yes'

ALLOWED_HOSTS = ["127.0.0.1", "localhost", environ.get('PUBLIC_URL')]

# Secure cookies
https_enabled = environ.get('HTTPS', 'no') == 'yes'
CSRF_COOKIE_SECURE = https_enabled
SESSION_COOKIE_SECURE = https_enabled

# HSTS configuration
#   enable for 6 months
#   preload certificates
#   include subdomains in HSTS
SECURE_HSTS_SECONDS = 15778800 if https_enabled else None
SECURE_HSTS_PRELOAD = https_enabled
SECURE_HSTS_INCLUDE_SUBDOMAINS = https_enabled

# Redirect HTTP to HTTPS
SECURE_SSL_REDIRECT = https_enabled


# Application definition

INSTALLED_APPS = [
    'anymail',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mailgunner.urls'

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

WSGI_APPLICATION = 'mailgunner.wsgi.application'


# Default database configuration (for local development)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': '172.17.0.3',
        'PORT': '5432',
    }
}

# Load database config from environment
db_from_env = dj_database_url.config('DATABASE_URL', conn_max_age=600)
DATABASES['default'].update(db_from_env)


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Vancouver'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Mailer configuration
ANYMAIL = {
    'MAILGUN_API_KEY': environ.get('MAILGUN_API_KEY'),
    'MAILGUN_SENDER_DOMAIN': environ.get('MAILGUN_DOMAIN'),
    'MAILGUN_WEBHOOK_SIGNING_KEY': environ.get('MAILGUN_WEBHOOK_SIGNING_KEY'),
    'WEBHOOK_SECRET': environ.get('WEBHOOK_SECRET'),
}
EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'
DEFAULT_FROM_EMAIL = 'hello@' + environ.get('MAILGUN_DOMAIN')
SERVER_EMAIL = 'mailgunner@' + environ.get('MAILGUN_DOMAIN')
