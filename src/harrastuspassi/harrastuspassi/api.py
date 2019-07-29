# -*- coding: utf-8 -*-

import logging
from django import forms
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


class HobbyFilter(filters.FilterSet):
  category = filters.ModelMultipleChoiceFilter(
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
