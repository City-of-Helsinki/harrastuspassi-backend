
# -*- coding: utf-8 -*-
#
# Copyright Haltu Oy, info@haltu.fi
# All rights reserved.
#

from django.contrib import admin


class UserAdminSite(admin.AdminSite):
  pass

site = UserAdminSite(name='useradmin')



# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2
