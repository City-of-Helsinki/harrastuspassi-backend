
# -*- coding: utf-8 -*-
#
# Copyright Haltu Oy, info@haltu.fi
# All rights reserved.
#

import logging
from django.views.generic import TemplateView

LOG = logging.getLogger(__name__)


class IndexView(TemplateView):
  template_name = 'harrastuspassi/views/index.html'


# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2
