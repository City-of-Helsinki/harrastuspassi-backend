
# -*- coding: utf-8 -*-

from django.urls import path, include
from rest_framework import routers
from harrastuspassi.api import HobbyViewSet, HobbyCategoryViewSet

router = routers.DefaultRouter()
router.register(r'hobbies', HobbyViewSet, 'hobby')
router.register(r'hobbycategories', HobbyCategoryViewSet)


urlpatterns = [
  path('api/', include(router.urls)),
  path('mobile-api/', include(router.urls))
]


# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2
