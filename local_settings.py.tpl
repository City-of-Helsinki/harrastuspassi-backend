# -*- coding: utf-8 -*-
from project.settings import *

DEBUG = True

SITE_ID = 1

SECRET_KEY = '!'

ALLOWED_HOSTS = ['*']

AUTH_PASSWORD_VALIDATORS = []

SECURE_SSL_REDIRECT = False

DATABASES = {
  'default': {
    'ENGINE': 'django.contrib.gis.db.backends.postgis',
    'HOST': 'postgresql',
    'PORT': '5432',
    'NAME': 'bergenia',
    'USER': 'bergenia',
    'PASSWORD': 'bergenia',
    'OPTIONS': {'sslmode': 'disable', },
    'ATOMIC_REQUESTS': True,
  }
}


STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2
