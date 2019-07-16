
# -*- coding: utf-8 -*-
#
# Copyright Haltu Oy, info@haltu.fi
# All rights reserved.
#

from django.urls import path
from django.contrib.auth.decorators import login_required
from harrastuspassi.views import IndexView

urlpatterns = [
  path('', IndexView.as_view()),
]


# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2
