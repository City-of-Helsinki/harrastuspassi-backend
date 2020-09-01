
# -*- coding: utf-8 -*-
import os
from django.urls import include, path, re_path
from rest_framework import routers
from harrastuspassi.api import (
    BenefitViewSet,
    HobbyViewSet,
    HobbyCategoryViewSet,
    HobbyEventViewSet,
    OrganizerViewSet,
    LocationViewSet,
    PromotionViewSet,
)

DEBUG = os.environ.get('DEBUG', False)

router = routers.DefaultRouter()
router.register(r'hobbies', HobbyViewSet, 'hobby')
router.register(r'hobbycategories', HobbyCategoryViewSet)
router.register(r'hobbyevents', HobbyEventViewSet, 'hobbyevent')
router.register(r'organizers', OrganizerViewSet)
router.register(r'locations', LocationViewSet, 'location')
router.register(r'promotions', PromotionViewSet)
router.register(r'benefits', BenefitViewSet)


public_urlpatterns = [
    re_path('api/(?P<version>(pre1|pre2|v1))/', include(router.urls,)),
    path('api/', include(router.urls)),  # DEPRECATED, used by mobile v0.2.0
]

internal_urlpatterns = [
    re_path('mobile-api/(?P<version>(pre1|pre2|v1))/', include(router.urls)),
    path('mobile-api/', include(router.urls)),  # DEPRECATED, used by mobile v0.2.0
]

if DEBUG:
    import debug_toolbar
    internal_urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))

urlpatterns = public_urlpatterns + internal_urlpatterns
