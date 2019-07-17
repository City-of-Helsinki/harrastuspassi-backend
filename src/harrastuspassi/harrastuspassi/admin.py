
# -*- coding: utf-8 -*-
#
# Copyright Haltu Oy, info@haltu.fi
# All rights reserved.
#

from django.contrib import admin
from harrastuspassi.models import Hobby, Location

class SysAdminSite(admin.AdminSite):


  def has_permission(self, request):
    return request.user.is_active and request.user.is_staff and request.user.is_superuser

class HobbyAdmin(admin.ModelAdmin):
  pass

class LocationAdmin(admin.ModelAdmin):
  pass

site = SysAdminSite()
admin.site.register(Hobby, HobbyAdmin)
admin.site.register(Location, LocationAdmin)


# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2
