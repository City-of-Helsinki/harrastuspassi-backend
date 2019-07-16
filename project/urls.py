# -*- coding: utf-8 -*-
#
# Copyright Haltu Oy, info@haltu.fi
# All rights reserved.
#

from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
  url(r'', include('harrastuspassi.urls')),
  url(r'^sysadmin/', admin.site.urls),
]


# Serve static and media files from Django
# Django will disable these automatically when DEBUG = False
urlpatterns += staticfiles_urlpatterns()

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2
