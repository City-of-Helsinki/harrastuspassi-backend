# -*- coding: utf-8 -*-

import logging
import requests
from itertools import chain
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django_filters import rest_framework as filters
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.views import APIView
from harrastuspassi import settings
from harrastuspassi.models import Hobby, HobbyCategory, HobbyEvent
from harrastuspassi.serializers import (
    HobbySerializer, HobbyDetailSerializer, HobbyCategorySerializer, HobbyEventSerializer
)

LOG = logging.getLogger(__name__)


class IsCreatorOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has a `created_by` attribute.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Instance must have an attribute named `created_by`.
        return obj.created_by == request.user


class ExtraDataSchema(AutoSchema):
    """ Schema describing the include parameter from ExtraDataMixin for serializers """
    def __init__(self, *args, **kwargs):
        self.include_description = kwargs.pop('include_description')
        if self.include_description is None:
            self.include_description = 'Include extra data in the response'
        super().__init__(*args, **kwargs)

    def get_operation(self, path, method, *args, **kwargs):
        operation = super().get_operation(path, method, *args, **kwargs)
        if method == 'GET':
            include_parameter = {
                'description': self.include_description,
                'in': 'query',
                'name': 'include',
                'required': False,
                'schema': {'type': 'string'},
            }
            operation['parameters'].append(include_parameter)
        return operation


class HobbyCategoryFilter(filters.FilterSet):
    parent = filters.ModelChoiceFilter(null_label='Root category', queryset=HobbyCategory.objects.all())


class HobbyCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = HobbyCategoryFilter
    queryset = HobbyCategory.objects.all()
    schema = ExtraDataSchema(
        include_description=('Include extra data in the response. Multiple include parameters are supported.'
                             ' Possible options: child_categories'))
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


class HobbyViewSet(viewsets.ModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = HobbyFilter
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsCreatorOrReadOnly)
    queryset = Hobby.objects.all().select_related('location', 'organizer')
    schema = ExtraDataSchema(
        include_description=('Include extra data in the response. Multiple include parameters are supported.'
                             ' Possible options: location_detail, organizer_detail'))
    serializer_class = HobbySerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def retrieve(self, request, pk=None):
        queryset = Hobby.objects.all()
        hobby = get_object_or_404(queryset, pk=pk)
        serializer = HobbyDetailSerializer(hobby)
        return Response(serializer.data)


class HobbyEventFilter(filters.FilterSet):
    category = HierarchyModelMultipleChoiceFilter(
        field_name='hobby__category', queryset=HobbyCategory.objects.all(),
        label=_('HobbyCategory id'),
    )
    hobby = filters.ModelChoiceFilter(field_name='hobby', queryset=Hobby.objects.all(), label=_('Hobby id'))
    start_date_from = filters.DateFilter(field_name='start_date', lookup_expr='gte',
                                         label=_(f'Return results starting from given date (inclusive).'
                                                 f' Use ISO 8601 date format, eg. "2020-01-30".'))
    start_date_to = filters.DateFilter(field_name='start_date', lookup_expr='lte',
                                       label=_(f'Return results with starting date up to given date (inclusive).'
                                               f' Use ISO 8601 date format, eg. "2020-01-30".'))
    start_time_from = filters.TimeFilter(field_name='start_time', lookup_expr='gte',
                                         label=_(f'Return results with starting time from given time (inclusive)'
                                                 f' Eg. "19:00".'))
    start_time_to = filters.TimeFilter(field_name='start_time', lookup_expr='lte',
                                       label=_(f'Return results with starting time up to given time (inclusive)'
                                               f' Eg. "21:00".'))
    start_weekday = filters.MultipleChoiceFilter(choices=HobbyEvent.DAY_OF_WEEK_CHOICES,
                                                 label=_(f'Return results with starting date in given weekday.'
                                                         f' Enter a number from 1 to 7. Use ISO 8601 weekdays:'
                                                         f' 1=Monday, 7=Sunday.'))

    class Meta:
        model = HobbyEvent
        fields = ['category', 'hobby', 'start_date_from', 'start_date_to',
                  'start_time_from', 'start_time_to', 'start_weekday']


class HobbyEventViewSet(viewsets.ReadOnlyModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = HobbyEventFilter
    queryset = HobbyEvent.objects.all().select_related('hobby__location', 'hobby__organizer')
    schema = ExtraDataSchema(
        include_description=('Include extra data in the response. Multiple include parameters are supported.'
                             ' Possible options: hobby_detail'))
    serializer_class = HobbyEventSerializer


class GeocodingAPIView(APIView):
    """ Provides geocoding service for the mobile application """
    def get(self, request, format=None):
        address = request.GET.get('address')
        if address:
            payload = {
                'searchtext': address,
                'app_id': settings.HERE_APP_ID,
                'app_code': settings.HERE_APP_CODE,
            }
            url = 'https://geocoder.api.here.com/6.2/geocode.json'
            try:
                response = requests.get(url, params=payload, timeout=settings.DEFAULT_REQUESTS_TIMEOUT)
                response.raise_for_status()
                location_data = response.json()
            except requests.exceptions.RequestException:
                LOG.error('Invalid response from GeoCoding API',
                          extra={'data': {
                              'status_code': response.status_code, 'location_data': repr(response.content)}})
                return Response(self.format_response([]))
            LOG.debug('Received location data', extra={'data': {'location_data': repr(location_data)}})
            location_views = location_data['Response']['View']
            if len(location_views) == 0:
                LOG.warning('No location results for address', extra={'data': {'url': response.url}})
                return Response(self.format_response([]))
            else:
                location_results = location_views[0]['Result']
                results = [{
                    'latitude': result['Location']['DisplayPosition']['Latitude'],
                    'longitude': result['Location']['DisplayPosition']['Longitude'],
                } for result in location_results]
                return Response(self.format_response(results))

    def format_response(self, result_list):
        return {
            'result_count': len(result_list),
            'results': result_list
        }
