
# -*- coding: utf-8 -*-

from django.conf import settings

AUTH_USER_MODEL = settings.AUTH_USER_MODEL
LINKED_COURSES_URL = getattr(settings, 'HARRASTUSPASSI_LINKED_COURSES_URL', 'https://api.hel.fi/linkedcourses/v1/event/')
