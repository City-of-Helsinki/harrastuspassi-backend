
# -*- coding: utf-8 -*-

import logging
from rest_framework import viewsets
from harrastuspassi.models import Hobby
from harrastuspassi.serializers import HobbySerializer

LOG = logging.getLogger(__name__)


class HobbyViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = Hobby.objects.all()
  serializer_class = HobbySerializer

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2
