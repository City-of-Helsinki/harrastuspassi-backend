
# -*- coding: utf-8 -*-

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from ..views.auth import TokenObtainPairView


urlpatterns = [
    path('auth/token/', TokenObtainPairView.as_view(), name='auth.token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='auth.token_refresh'),
]
