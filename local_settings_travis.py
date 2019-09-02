from project.settings import *

DEBUG = True

SECRET_KEY = "!"

ALLOWED_HOSTS = ["*"]

AUTH_PASSWORD_VALIDATORS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'harrastuspassi_travis_ci',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '5432',
        'ATOMIC_REQUESTS': True,
    }
}

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
