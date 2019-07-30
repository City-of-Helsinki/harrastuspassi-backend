# -*- coding: utf-8 -*-
from django.urls import path, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from project import settings

admin_urls = [
  path('sysadmin/', admin.site.urls),
]

app_urls = [
  path('', include('harrastuspassi.urls')),
  path('monitor/', include('health_check.urls'))
]

static_urls = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
static_urls += staticfiles_urlpatterns()

urlpatterns = admin_urls + app_urls + static_urls

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2
