
# -*- coding: utf-8 -*-
#
# Copyright Haltu Oy, info@haltu.fi
# All rights reserved.
#

from django.contrib import admin


class SysAdminSite(admin.AdminSite):


  def has_permission(self, request):
    return request.user.is_active and request.user.is_staff and request.user.is_superuser


site = SysAdminSite()



# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2
