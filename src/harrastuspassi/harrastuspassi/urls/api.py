
# -*- coding: utf-8 -*-

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

router = routers.DefaultRouter()
router.register(r'hobbies', HobbyViewSet, 'hobby')
router.register(r'hobbycategories', HobbyCategoryViewSet)
router.register(r'hobbyevents', HobbyEventViewSet)
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

urlpatterns = public_urlpatterns + internal_urlpatterns
