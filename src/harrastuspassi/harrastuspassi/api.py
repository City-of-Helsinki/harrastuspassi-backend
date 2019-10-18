# -*- coding: utf-8 -*-

import logging
from collections import defaultdict
from functools import wraps
from itertools import chain
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django_filters import rest_framework as filters
from django_filters.constants import EMPTY_VALUES
from rest_framework import permissions, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from harrastuspassi.models import Hobby, HobbyCategory, HobbyEvent
from harrastuspassi.serializers import (
    HobbySerializer, HobbyCategorySerializer, HobbyDetailSerializer, HobbyDetailSerializerPre1, HobbyEventSerializer,
    HobbySerializerPre1
)

LOG = logging.getLogger(__name__)


def dummy_filter(filter_callable):
    """
    Ignore filter method of Filter classes.
    Can be used for documentation-only params and custom non-field filters.
    """
    def wrapped_filter(*args, **kwargs):
        return wrapped_filter(*args, **kwargs)
    def noop_filter(self, qs, value):
        return qs
    wrapped_filter.filter = noop_filter
    return wraps(filter_callable)(wrapped_filter)


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


class NearestOrderingFilter(filters.OrderingFilter):
    def get_coordinates(self):
        errors = defaultdict(list)

        try:
            near_latitude = self.parent.data['near_latitude']
        except KeyError:
            errors['near_latitude'].append(_('This field is required when nearest ordering is used.'))
        try:
            near_longitude = self.parent.data['near_longitude']
        except KeyError:
            errors['near_longitude'].append(_('This field is required when nearest ordering is used.'))
        if errors:
            raise ValidationError(errors)

        try:
            near_latitude = float(near_latitude)
        except (TypeError, ValueError):
            errors['near_latitude'].append(_('Must be a float.'))
        try:
            near_longitude = float(near_longitude)
        except (TypeError, ValueError):
            errors['near_longitude'].append(_('Must be a float.'))
        if errors:
            raise ValidationError(errors)

        try:
            assert near_latitude >= -180.0
            assert near_latitude <= 180.0
        except AssertionError:
            errors['near_latitude'].append(_('Value must be within -180.0 and 180.0.'))
        try:
            assert near_longitude >= -90.0
            assert near_longitude <= 90.0
        except AssertionError:
            errors['near_longitude'].append(_('Value must be within -90.0 and 90.0.'))
        if errors:
            raise ValidationError(errors)

        return near_latitude, near_longitude

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        ordering = [self.get_ordering_value(param) for param in value]
        if 'distance_to_point' in ordering or '-distance_to_point' in ordering:
            near_latitude, near_longitude = self.get_coordinates()
            qs = qs.annotate_distance_to(near_latitude, near_longitude)
        return qs.order_by(*ordering)


class HobbyFilter(filters.FilterSet):
    category = HierarchyModelMultipleChoiceFilter(
        field_name='categories', queryset=HobbyCategory.objects.all(),
    )
    ordering = NearestOrderingFilter(
        fields=(
            # (field name, param name)
            ('distance_to_point', 'nearest'),
        ),
        field_labels={
            'distance_to_point': _('Nearest'),
        },
        label=_('Ordering. Choices: `nearest`')
    )
    near_latitude = dummy_filter(filters.NumberFilter(label=_('Near latitude. This field is required when `nearest` ordering is used.')))
    near_longitude = dummy_filter(filters.NumberFilter(label=_('Near longitude. This field is required when `nearest` ordering is used.')))

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

    def get_serializer_class(self):
        # TODO: DEPRECATE VERSION pre1
        if self.request.version == 'pre1':
            return HobbySerializerPre1
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def retrieve(self, request, pk=None):
        # TODO: DEPRECATE VERSION pre1
        if self.request.version == 'pre1':
            serializer_class = HobbyDetailSerializerPre1
        else:
            serializer_class = HobbyDetailSerializer
        queryset = Hobby.objects.all()
        hobby = get_object_or_404(queryset, pk=pk)
        serializer = serializer_class(hobby)
        return Response(serializer.data)


class HobbyEventFilter(filters.FilterSet):
    category = HierarchyModelMultipleChoiceFilter(
        field_name='hobby__categories', queryset=HobbyCategory.objects.all(),
        label=_('HobbyCategory id'),
    )
    ordering = NearestOrderingFilter(
        fields=(
            # (field name, param name)
            ('distance_to_point', 'nearest'),
        ),
        field_labels={
            'distance_to_point': _('Nearest'),
        },
        label=_('Ordering. Choices: `nearest`')
    )
    near_latitude = dummy_filter(filters.NumberFilter(label=_('Near latitude. This field is required when `nearest` ordering is used.')))
    near_longitude = dummy_filter(filters.NumberFilter(label=_('Near longitude. This field is required when `nearest` ordering is used.')))
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
