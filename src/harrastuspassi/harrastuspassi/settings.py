
# -*- coding: utf-8 -*-

from django.conf import settings

AUTH_USER_MODEL = settings.AUTH_USER_MODEL
DEFAULT_REQUESTS_TIMEOUT = 5
HERE_APP_ID = getattr(settings, 'HARRASTUSPASSI_HERE_APP_ID', '')
HERE_APP_CODE = getattr(settings, 'HARRASTUSPASSI_HERE_APP_CODE', '')
