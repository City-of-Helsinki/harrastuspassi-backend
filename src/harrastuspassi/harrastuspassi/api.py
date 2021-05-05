# -*- coding: utf-8 -*-

import datetime
import logging
from collections import defaultdict
from itertools import chain

from django.contrib.gis.measure import Distance
from django.db.models import F, Q
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django_filters import rest_framework as filters
from django_filters.constants import EMPTY_VALUES
from guardian.core import ObjectPermissionChecker
from guardian.ctypes import get_content_type
from guardian.shortcuts import get_objects_for_user
from rest_framework import permissions, viewsets, serializers
from rest_framework import filters as drf_filters
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema

from harrastuspassi import settings
from harrastuspassi.geocoding import get_coordinates_from_address

from harrastuspassi.models import (
    Benefit,
    Hobby,
    HobbyCategory,
    HobbyEvent,
    Location,
    Municipality,
    Organizer,
    Promotion,
)

from harrastuspassi.serializers import (
    BenefitSerializer,
    HobbyCategorySerializer,
    HobbyDetailSerializer,
    HobbyDetailSerializerPre1,
    HobbyEventSerializer,
    HobbySerializer,
    HobbySerializerPre1,
    LocationSerializer,
    LocationSerializerPre1,
    OrganizerSerializer,
    PromotionSerializer
)

from project.pagination import DefaultPagination

LOG = logging.getLogger(__name__)


def dummy_filter(filter_instance):
    """
    Ignore filter method of Filter classes.
    Can be used for documentation-only params and custom non-field filters.
    """
    def noop_filter(qs, value):
        return qs
    filter_instance.filter = noop_filter
    return filter_instance


class HasPermOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        ctype = get_content_type(obj)
        change_perm_name = f'change_{ctype}'
        return request.user.has_perm(change_perm_name, obj)


class PermissionPrefetchMixin:
    def get_serializer_context(self):
        context = super().get_serializer_context()
        queryset = self.get_queryset()
        if queryset:
            prefetched_permission_checker = ObjectPermissionChecker(self.request.user)
            prefetched_permission_checker.prefetch_perms(queryset)
            context['prefetched_permission_checker'] = prefetched_permission_checker
        return context


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


class HobbyEventSearchFilter(drf_filters.SearchFilter):
    """ Custom search filter that takes categories descendants into account """
    def filter_queryset(self, request, queryset, view):
        qs = super().filter_queryset(request, queryset, view)
        search_terms = self.get_search_terms(request)
        category_ids = []
        for search_term in search_terms:
            parent_categories_qs = HobbyCategory.objects.filter(
                Q(name_fi__icontains=search_term) |
                Q(name_en__icontains=search_term) |
                Q(name_sv__icontains=search_term)
            )
            parent_ids = list(parent_categories_qs.values_list('pk', flat=True))
            descendant_ids = list(parent_categories_qs.get_descendants(include_self=False).values_list('pk', flat=True))
            category_ids += parent_ids
            category_ids += descendant_ids
        if category_ids:
            try:
                qs |= queryset.filter(hobby__categories__in=category_ids)
            except AssertionError:
                # AssertionError: Cannot combine a unique query with a non-unique query.
                # Both queries must be distinct (unique query)
                qs |= queryset.filter(hobby__categories__in=category_ids).distinct()
            qs = qs.distinct()
        return qs


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

    def get_max_distance(self):
        errors = defaultdict(list)
        max_distance = self.parent.data.get('max_distance', None)
        if max_distance is not None:
            try:
                max_distance = int(max_distance)
            except ValueError:
                errors['max_distance'].append(_('Must be an integer.'))
        if errors:
            raise ValidationError(errors)
        return max_distance

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        ordering = [self.get_ordering_value(param) for param in value]
        if 'geometrydistance_to_point' in ordering or '-geometrydistance_to_point' in ordering:
            near_latitude, near_longitude = self.get_coordinates()
            qs = qs.annotate_geometrydistance_to(near_latitude, near_longitude)
            qs = qs.annotate_distance_to(near_latitude, near_longitude)
        qs = qs.order_by(*ordering)
        max_distance = self.get_max_distance()
        if max_distance is not None:
            qs = qs.filter(distance_to_point__lte=Distance(km=max_distance))
        return qs


class HobbyFilter(filters.FilterSet):
    category = HierarchyModelMultipleChoiceFilter(
        field_name='categories', queryset=HobbyCategory.objects.all(),
    )
    editable_only = filters.BooleanFilter(method='filter_editable', label=_('Show editable only'))
    ordering = NearestOrderingFilter(
        fields=(
            # (field name, param name)
            ('geometrydistance_to_point', 'nearest'),
        ),
        field_labels={
            'geometrydistance_to_point': _('Nearest'),
        },
        label=_('Ordering. Choices: `nearest`')
    )
    near_latitude = dummy_filter(filters.NumberFilter(label=_('Near latitude. This field is required when `nearest` ordering is used.')))
    near_longitude = dummy_filter(filters.NumberFilter(label=_('Near longitude. This field is required when `nearest` ordering is used.')))
    max_distance = dummy_filter(filters.NumberFilter(label=_('Max distance in kilometers. Can only be used with `nearest` ordering.')))
    price_type = filters.CharFilter(method='filter_price_type', label=_('Filter Hobbies by price type'))

    class Meta:
        model = Hobby
        fields = ['category']

    def filter_editable(self, queryset, name, value):
        is_filtering_requested = value
        if not is_filtering_requested:
            return queryset
        if self.request.user.is_authenticated:
            return get_objects_for_user(self.request.user, 'change_hobby', self.queryset)
        else:
            return self.queryset.none()

    def filter_price_type(self, queryset, name, value):
        value_in_price_type_choices = any(value == price_type for price_type, label in Hobby.PRICE_TYPE_CHOICES)
        if value_in_price_type_choices:
            queryset = queryset.filter(price_type=value)
        return queryset


class HobbyViewSet(PermissionPrefetchMixin, viewsets.ModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = HobbyFilter
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, HasPermOrReadOnly)
    queryset = Hobby.objects.all().select_related('location', 'organizer')
    schema = ExtraDataSchema(
        include_description=('Include extra data in the response. Multiple include parameters are supported.'
                             ' Possible options: location_detail, organizer_detail'))
    serializer_class = HobbySerializer
    pagination_class = DefaultPagination

    def get_serializer_class(self):
        # TODO: DEPRECATE VERSION pre1
        if self.request.version == 'pre1':
            return HobbySerializerPre1
        return self.serializer_class

    @property
    def paginator(self):
        if self.request.version in ['pre1', 'pre2']:
            return None
        else:
            return super().paginator

    def perform_create(self, serializer):
        municipality = Municipality.get_current_municipality_for_moderator(self.request.user)
        serializer.save(created_by=self.request.user, municipality=municipality)


class HobbyEventFilter(filters.FilterSet):
    category = HierarchyModelMultipleChoiceFilter(
        field_name='hobby__categories', queryset=HobbyCategory.objects.all(),
        label=_('HobbyCategory id'),
    )
    ordering = NearestOrderingFilter(
        fields=(
            # (field name, param name)
            ('geometrydistance_to_point', 'nearest'),
            ('start_date', 'start_date'),
        ),
        field_labels={
            'geometrydistance_to_point': _('Nearest'),
            'start_date': _('Start date'),
        },
        label=_('Ordering. Choices: `nearest`, `start_date`')
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
    exclude_past_events = filters.BooleanFilter(method='filter_past_events', label=_('Show upcoming only'))
    price_type = filters.CharFilter(method='filter_price_type', label=_('Filter HobbyEvents by price type'))

    class Meta:
        model = HobbyEvent
        fields = ['category', 'hobby', 'start_date_from', 'start_date_to',
                  'start_time_from', 'start_time_to', 'start_weekday']

    def filter_past_events(self, queryset, name, value):
        is_filtering_requested = value
        date_is_before_today = Q(end_date__lt=datetime.date.today())
        date_is_today_but_time_is_in_past = Q(end_date=datetime.date.today()) & Q(end_time__lt=datetime.datetime.now().time())
        if is_filtering_requested:
            return queryset.exclude(date_is_before_today | date_is_today_but_time_is_in_past)
        else:
            return queryset

    def filter_price_type(self, queryset, name, value):
        value_in_price_type_choices = any(value == price_type for price_type, label in Hobby.PRICE_TYPE_CHOICES)
        if value_in_price_type_choices:
            queryset = queryset.filter(hobby__price_type=value)
        return queryset


class HobbyEventViewSet(viewsets.ModelViewSet):
    filter_backends = (filters.DjangoFilterBackend, HobbyEventSearchFilter)
    filterset_class = HobbyEventFilter
    schema = ExtraDataSchema(
        include_description=('Include extra data in the response. Multiple include parameters are supported.'
                             ' Possible options: hobby_detail'))
    serializer_class = HobbyEventSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = DefaultPagination
    search_fields = ['hobby__name', 'hobby__description']

    def get_queryset(self):
        hobby_in_query_params = self.request.query_params.get('hobby', None)
        queryset = HobbyEvent.objects.all()
        # Hobby may have dozens of events, so only return relevant for the list view
        if self.action == 'list' and not hobby_in_query_params:
            queryset = queryset.filter(hobby_via_next_event__isnull=False)
        return queryset.select_related('hobby__location', 'hobby__organizer')

    @property
    def paginator(self):
        if self.request.version in ['pre1', 'pre2']:
            return None
        else:
            return super().paginator


class OrganizerViewSet(viewsets.ModelViewSet):
    queryset = Organizer.objects.all()
    serializer_class = OrganizerSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        qs = Organizer.objects.all()
        if self.request.user.is_authenticated:
            return get_objects_for_user(self.request.user, 'change_organizer', qs)
        return qs.order_by('name')

    def perform_create(self, serializer):
        municipality = Municipality.get_current_municipality_for_moderator(self.request.user)        
        serializer.save(created_by=self.request.user, municipality=municipality)


class LocationViewSet(viewsets.ModelViewSet):
    serializer_class = LocationSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        qs = Location.objects.all()
        if self.request.user.is_authenticated:
            return get_objects_for_user(self.request.user, 'change_location', qs)
        return qs.order_by('name')

    def get_serializer_class(self):
        # TODO: DEPRECATE VERSION pre1
        if self.request.version == 'pre1':
            return LocationSerializerPre1
        return self.serializer_class

    def perform_create(self, serializer):
        municipality = Municipality.get_current_municipality_for_moderator(self.request.user)
        if settings.GOOGLE_GEOCODING_API_KEY and 'coordinates' not in self.request.data:
            address = self.request.data.get('address', '')
            zip_code = self.request.data.get('zip_code', '')
            city = self.request.data.get('city', '')
            formatted_address = f'{address},+{zip_code}+{city}'
            try:
                coordinates = get_coordinates_from_address(formatted_address)
            except APIException:
                raise serializers.ValidationError('This address could not be geocoded. Please confirm your address is right, or try again later.')
            serializer.save(created_by=self.request.user, municipality=municipality, coordinates=coordinates)
        else:
            serializer.save(created_by=self.request.user, municipality=municipality)


class PromotionFilter(filters.FilterSet):
    exclude_past_events = filters.BooleanFilter(method='filter_past_events', label=_('Show upcoming only'))
    usable_only = filters.BooleanFilter(method='filter_used_promotions', label=_('Show only usable promotions'))
    editable_only = filters.BooleanFilter(method='filter_editable', label=_('Show editable only'))
    ordering = NearestOrderingFilter(
        fields=(
            # (field name, param name)
            ('geometrydistance_to_point', 'nearest'),
        ),
        field_labels={
            'geometrydistance_to_point': _('Nearest'),
        },
        label=_('Ordering. Choices: `nearest`')
    )
    near_latitude = dummy_filter(filters.NumberFilter(label=_('Near latitude. This field is required when `nearest` ordering is used.')))
    near_longitude = dummy_filter(filters.NumberFilter(label=_('Near longitude. This field is required when `nearest` ordering is used.')))

    def filter_past_events(self, queryset, name, value):
        is_filtering_requested = value
        date_is_before_today = Q(end_date__lt=datetime.date.today())
        date_is_today_but_time_is_in_past = Q(end_date=datetime.date.today()) & Q(end_time__lt=datetime.datetime.now().time())
        if is_filtering_requested:
            return queryset.exclude(date_is_before_today | date_is_today_but_time_is_in_past)
        else:
            return queryset

    def filter_used_promotions(self, queryset, name, value):
        is_filtering_requested = value
        if is_filtering_requested:
            return queryset.filter(available_count__gt=F('used_count'))
        return queryset

    def filter_editable(self, queryset, name, value):
        is_filtering_requested = value
        if not is_filtering_requested:
            return queryset
        if self.request.user.is_authenticated:
            return get_objects_for_user(self.request.user, 'change_promotion', self.queryset)
        else:
            return self.queryset.none()


class PromotionViewSet(viewsets.ModelViewSet):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    filter_backends = (filters.DjangoFilterBackend, drf_filters.SearchFilter)
    filterset_class = PromotionFilter
    search_fields = ['name', 'description']

    def perform_create(self, serializer):
        municipality = Municipality.get_current_municipality_for_moderator(self.request.user)
        serializer.save(municipality=municipality)


class BenefitViewSet(viewsets.ModelViewSet):
    queryset = Benefit.objects.all()
    serializer_class = BenefitSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
