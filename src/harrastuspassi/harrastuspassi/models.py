
# -*- coding: utf-8 -*-
import logging
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.db.models.functions import GeoFunc
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.expressions import Func
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from harrastuspassi import settings

LOG = logging.getLogger(__name__)


# SRID 4326 - Spatial Reference System Identifier number 4326.
# EPSG:4326 - It's the same thing, but EPSG is the name of the authority maintaining an SRID reference.
# WGS 84 - World Geodetic System from 1984. It's the coordinate system used in GPS.
#
# 4326 is the identifier number (SRID) for WGS 84 in the EPSG reference.
# So in summary SRID 4326 == EPSG:4326 == WGS 84 == "GPS coordinates".
#
# The coordinates in this coordinate system are numbers in the range of
# -90.0000 to 90.0000 for latitude and -180.0000 to 180.0000 for longitude.
COORDINATE_SYSTEM_ID = 4326


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(editable=False, default=timezone.now)
    updated_at = models.DateTimeField(editable=False, auto_now=True)

    class Meta:
        abstract = True


class ExternalDataModel(models.Model):
    data_source = models.CharField(verbose_name=_('External data source'), max_length=256, blank=True, default='')
    origin_id = models.CharField(verbose_name=_('ID in external data source'), max_length=128, blank=True, default='')

    class Meta:
        abstract = True


class GeometryDistance(GeoFunc):
    # Backported from Django 3.0
    # GeometryDistance allows spatial sorting using spatial indexes
    output_field = models.FloatField()
    arity = 2
    function = ''
    arg_joiner = ' <-> '
    geom_param_pos = (0, 1)

    def as_sql(self, *args, **kwargs):
        return Func.as_sql(self, *args, **kwargs)


class DistanceMixin:
    coordinates_field = 'coordinates'

    def annotate_distance_to(self, lat, lon):
        x = lon
        y = lat
        point = Point(x, y, srid=COORDINATE_SYSTEM_ID)
        return self.annotate(distance_to_point=GeometryDistance(self.coordinates_field, point))

    def order_by_distance_to(self, lat, lon):
        qs = self.annotate_distance_to(lat, lon)
        qs = qs.order_by('distance_to_point')
        return qs


class LocationQuerySet(DistanceMixin, models.QuerySet):
    coordinates_field = 'coordinates'


class Location(ExternalDataModel, TimestampedModel):
    name = models.CharField(max_length=256, blank=True)
    address = models.CharField(max_length=256, blank=True)
    zip_code = models.CharField(max_length=5, blank=True)
    city = models.CharField(max_length=64, blank=True)
    coordinates = gis_models.PointField(null=True, blank=True, srid=COORDINATE_SYSTEM_ID)

    objects = LocationQuerySet.as_manager()

    @property
    def lat(self):
        return self.coordinates.y if self.coordinates else None

    @property
    def lon(self):
        return self.coordinates.x if self.coordinates else None

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()

        if not self.name and not self.city and not self.coordinates:
            raise ValidationError('One of the following fields is required: name, city or coordinates')


class Organizer(ExternalDataModel, TimestampedModel):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class HobbyCategory(MPTTModel, ExternalDataModel, TimestampedModel):
    name = models.CharField(max_length=256)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = 'Hobby categories'

    def __str__(self):
        return self.name


class HobbyQuerySet(DistanceMixin, models.QuerySet):
    coordinates_field = 'location__coordinates'


class Hobby(ExternalDataModel, TimestampedModel):
    name = models.CharField(max_length=1024)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    cover_image = models.ImageField(upload_to='hobby_images', null=True, blank=True)
    description = models.TextField(blank=True)
    organizer = models.ForeignKey(Organizer, null=True, blank=True, on_delete=models.CASCADE)
    categories = models.ManyToManyField(HobbyCategory, blank=True, related_name='hobbies', verbose_name=_('Categories'))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    objects = HobbyQuerySet.as_manager()

    class Meta:
        ordering = ('id',)
        verbose_name_plural = 'Hobbies'
        get_latest_by = 'created_at'

    def __str__(self):
        return self.name


class HobbyEventQuerySet(DistanceMixin, models.QuerySet):
    coordinates_field = 'hobby__location__coordinates'


class HobbyEvent(ExternalDataModel, TimestampedModel):
    """ An event in time when a hobby takes place """
    DAY_OF_WEEK_CHOICES = (
        (1, _('Monday')),
        (2, _('Tuesday')),
        (3, _('Wednesday')),
        (4, _('Thursday')),
        (5, _('Friday')),
        (6, _('Saturday')),
        (7, _('Sunday')),
    )
    hobby = models.ForeignKey(Hobby, related_name='events', verbose_name=_('Hobby'),
                              null=False, on_delete=models.CASCADE)
    start_date = models.DateField(blank=False, null=False, verbose_name=_('Start date'))
    start_time = models.TimeField(blank=False, null=False, verbose_name=_('Start time'))
    # note that ISO 8601 weekdays are used in start_weekday: 1=Monday, 7=Sunday
    start_weekday = models.PositiveSmallIntegerField(default=0, choices=DAY_OF_WEEK_CHOICES,
                                                     verbose_name=_('Start weekday'))
    end_date = models.DateField(blank=False, null=False, verbose_name=_('End date'))
    end_time = models.TimeField(blank=False, null=False, verbose_name=_('End time'))

    objects = HobbyEventQuerySet.as_manager()

    class Meta:
        ordering = ('start_date', 'start_time')
        verbose_name = 'Hobby Event'

    def save(self, *args, **kwargs):
        # precalculate ISO 8601 day of week for cheaper querying
        self.start_weekday = self.start_date.isoweekday()
        return super().save(*args, **kwargs)

    def __str__(self):
        if self.start_date != self.end_date:
            return f'{self.hobby.name} {self.start_date} - {self.end_date}'
        else:
            return f'{self.hobby.name} {self.start_date}'


class Promotion(TimestampedModel):
    hobby = models.ForeignKey(Hobby, on_delete=models.CASCADE)
    name = models.CharField(max_length=1024)
    description = models.TextField()
    start_date = models.DateField(blank=False, null=False, verbose_name=_('Start date'))
    start_time = models.TimeField(blank=False, null=False, verbose_name=_('Start time'))
    end_date = models.DateField(blank=False, null=False, verbose_name=_('End date'))
    end_time = models.TimeField(blank=False, null=False, verbose_name=_('End time'))
    cover_image = models.ImageField(upload_to='promo_images', null=True, blank=True)