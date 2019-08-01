
# -*- coding: utf-8 -*-

from django.urls import path, include
from rest_framework import routers
from harrastuspassi.api import HobbyViewSet, HobbyCategoryViewSet

router = routers.DefaultRouter()
router.register(r'hobbies', HobbyViewSet, 'hobby')
router.register(r'hobbycategories', HobbyCategoryViewSet)


public_urlpatterns = [
    path('api/', include(router.urls)),
]

internal_urlpatterns = [
    path('mobile-api/', include(router.urls)),
]

urlpatterns = public_urlpatterns + internal_urlpatterns
