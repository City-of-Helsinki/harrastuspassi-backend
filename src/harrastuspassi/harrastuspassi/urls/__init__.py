
# -*- coding: utf-8 -*-

from .auth import urlpatterns as auth_urlpatterns
from .api import urlpatterns as api_urlpatterns

urlpatterns = auth_urlpatterns + api_urlpatterns
