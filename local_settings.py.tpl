from project.settings import *

DEBUG = True

SECRET_KEY = '!'

ALLOWED_HOSTS = ['*']

AUTH_PASSWORD_VALIDATORS = []

DATABASES = {
  'default': {
    'ENGINE': 'django.contrib.gis.db.backends.postgis',
    'HOST': 'postgresql',
    'PORT': '5432',
    'NAME': 'heliconia',
    'USER': 'heliconia',
    'PASSWORD': 'heliconia',
    'OPTIONS': {'sslmode': 'disable', },
    'ATOMIC_REQUESTS': True,
  }
}


STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
