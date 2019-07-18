
# -*- coding: utf-8 -*-

from django.urls import path, include
from rest_framework import routers
from harrastuspassi.views import HobbyViewSet

router = routers.DefaultRouter()
router.register(r'hobbies', HobbyViewSet, 'hobby')


urlpatterns = [
  path('api/', include(router.urls)),
  path('mobile-api/', include(router.urls))
]


# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2
