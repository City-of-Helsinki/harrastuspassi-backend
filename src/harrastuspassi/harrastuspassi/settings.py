
# -*- coding: utf-8 -*-

from django.conf import settings

AUTH_USER_MODEL = settings.AUTH_USER_MODEL
DEFAULT_REQUESTS_TIMEOUT = 5
GOOGLE_GEOCODING_API_KEY = getattr(settings, 'HARRASTUSPASSI_GOOGLE_GEOCODING_API_KEY', '')

#  Keyword used in the Helmet import is marking the events that are allowed to be shown in Harrastuspassi
HELMET_URL = getattr(settings,
                     'HARRASTUSPASSI_HELMET_URL',
                     'https://api.hel.fi/linkedevents/v1/event/?keyword=helmet:11997')
LINKED_COURSES_URL = getattr(settings, 'HARRASTUSPASSI_LINKED_COURSES_URL',
                             'https://api.hel.fi/linkedcourses/v1/event/')
LIPAS_URL = getattr(settings, 'HARRASTUSPASSI_LIPAS_URL',
                    'http://lipas.cc.jyu.fi/api/sports-places/')
LIPPUPISTE_URL = getattr(settings, 'HARRASTUSPASSI_LIPPPUPISTE_URL',
                         'https://api.hel.fi/linkedevents/v1/event/?data_source=lippupiste')
#  Filtering by the audience keywords:
#  Included: yso:p11617 - nuoriso, yso:p16486 - opiskelijat
#  Excluded: yso:p4354 - lapset, yso:p13050 - lapsiperheet, yso:p16485 - peruskoululaiset, yso:p20513 - vauvaperheet
LINKEDEVENTS_URL = getattr(settings, 'HARRASTUSPASSI_LINKEDEVENTS_URL',
                           'https://api.hel.fi/linkedevents/v1/event/?keyword=yso:p11617,yso:p16486&keyword!=yso:p4354,yso:p13050,yso:p16485,yso:p20513')
