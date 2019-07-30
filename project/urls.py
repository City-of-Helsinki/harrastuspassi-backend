# -*- coding: utf-8 -*-

from django.urls import include, path
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from rest_framework.schemas import get_schema_view
from project import settings

admin_urls = [
  path('sysadmin/', admin.site.urls),
]

app_urls = [
  path('', include('harrastuspassi.urls')),
  path('openapi', get_schema_view(
    title="Harrastuspassi",
    description="API documentation"
  ), name='openapi-schema'),
]

static_urls = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
static_urls += staticfiles_urlpatterns()

urlpatterns = admin_urls + app_urls + static_urls

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2
