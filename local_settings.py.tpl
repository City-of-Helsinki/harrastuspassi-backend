# -*- coding: utf-8 -*-
from project.settings import *

DEBUG = True

SITE_ID = 1

SECRET_KEY = '!'

INTERNAL_IPS = ['127.0.0.1']
ALLOWED_HOSTS = ['*']

AUTH_PASSWORD_VALIDATORS = []

SECURE_SSL_REDIRECT = False

INSTALLED_APPS.extend(['debug_toolbar', 'django_extensions'])

MIDDLEWARE.insert(2, 'debug_toolbar.middleware.DebugToolbarMiddleware')


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'HOST': 'localhost',
        'PORT': '5432',
        'NAME': 'bergenia',
        'USER': 'bergenia',
        'PASSWORD': 'bergenia',
        'OPTIONS': {'sslmode': 'disable', },
        'ATOMIC_REQUESTS': True,
    }
}


STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
