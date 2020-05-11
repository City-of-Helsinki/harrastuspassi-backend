
# -*- coding: utf-8 -*-

from django.conf import settings

AUTH_USER_MODEL = settings.AUTH_USER_MODEL
LINKED_COURSES_URL = getattr(settings, 'HARRASTUSPASSI_LINKED_COURSES_URL', 'https://api.hel.fi/linkedcourses/v1/event/')
LIPAS_URL = getattr(settings, 'HARRASTUSPASSI_LIPAS_URL', 'http://lipas.cc.jyu.fi/api/sports-places/')
DEFAULT_REQUESTS_TIMEOUT = 5
GOOGLE_GEOCODING_API_KEY = getattr(settings, 'HARRASTUSPASSI_GOOGLE_GEOCODING_API_KEY', '')
