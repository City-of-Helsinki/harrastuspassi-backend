# -*- coding: utf-8 -*-

import logging
from itertools import chain
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.response import Response
from harrastuspassi.models import Hobby, HobbyCategory
from harrastuspassi.serializers import HobbySerializer, HobbyDetailSerializer, HobbyCategorySerializer

LOG = logging.getLogger(__name__)


class HobbyCategoryViewSet(viewsets.ReadOnlyModelViewSet):
  queryset = HobbyCategory.objects.all()
  serializer_class = HobbyCategorySerializer


class HierarchyModelMultipleChoiceFilter(filters.ModelMultipleChoiceFilter):
  """ Filters using the given object and it's children. Use with MPTT models. """
  def filter(self, qs, value):
    # qs is the initial list of objects to be filtered
    # value is a list of objects to be used for filtering
    values_with_children = chain.from_iterable(
      [obj.get_descendants(include_self=True) if hasattr(obj, 'get_descendants') else [obj] for obj in value]
    )
    return super().filter(qs, list(values_with_children))


class HobbyFilter(filters.FilterSet):
  category = HierarchyModelMultipleChoiceFilter(
    queryset=HobbyCategory.objects.all(),
  )

  class Meta:
    model = Hobby
    fields = ['category']


class HobbyViewSet(viewsets.ReadOnlyModelViewSet):
  filter_backends = (filters.DjangoFilterBackend,)
  filterset_class = HobbyFilter
  queryset = Hobby.objects.all()
  serializer_class = HobbySerializer

  def retrieve(self, request, pk=None):
    queryset = Hobby.objects.all()
    hobby = get_object_or_404(queryset, pk=pk)
    serializer = HobbyDetailSerializer(hobby)
    return Response(serializer.data)

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2
