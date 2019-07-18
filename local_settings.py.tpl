from project.settings import *

DEBUG = True

SECRET_KEY = '!'

ALLOWED_HOSTS = ['*']

AUTH_PASSWORD_VALIDATORS = []

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': '',
    'USER': '',
    'PASSWORD': '',
    'HOST': 'localhost',
    'PORT': '5432',
  }
}

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'