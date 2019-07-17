
# -*- coding: utf-8 -*-
#
# Copyright Haltu Oy, info@haltu.fi
# All rights reserved.
#

from django.urls import path, include
from rest_framework import routers
from harrastuspassi.views import HobbyViewSet

router = routers.DefaultRouter()
router.register(r'hobbies', HobbyViewSet) 

urlpatterns = [
  path('', include(router.urls)),
]


# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2
