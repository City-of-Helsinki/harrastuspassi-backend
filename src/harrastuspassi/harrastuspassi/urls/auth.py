
# -*- coding: utf-8 -*-

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from ..views.auth import TokenObtainPairView


urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='auth.token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='auth.token_refresh'),
]
