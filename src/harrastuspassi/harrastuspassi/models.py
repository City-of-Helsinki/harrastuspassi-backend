
# -*- coding: utf-8 -*-
import logging
import datetime
import os
from copy import copy
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.db.models.functions import GeoFunc, Distance
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F
from django.db.models.expressions import Func
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
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
        return self.annotate(distance_to_point=Distance(self.coordinates_field, point))

    def annotate_geometrydistance_to(self, lat, lon):
        x = lon
        y = lat
        point = Point(x, y, srid=COORDINATE_SYSTEM_ID)
        return self.annotate(geometrydistance_to_point=GeometryDistance(self.coordinates_field, point))

    def order_by_distance_to(self, lat, lon):
        qs = self.annotate_geometrydistance_to(lat, lon)
        qs = qs.order_by('geometrydistance_to_point')
        return qs


class LocationQuerySet(DistanceMixin, models.QuerySet):
    coordinates_field = 'coordinates'


class Municipality(TimestampedModel):
    name = models.CharField(max_length=256, verbose_name='Municipality')
    moderators = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
                                        related_name='municipalities_where_moderator',
                                        verbose_name=_('Moderators'))

    @classmethod
    def get_current_municipality_for_moderator(self, user):
        return user.municipalities_where_moderator.first()

    def __str__(self):
        return self.name


class Location(ExternalDataModel, TimestampedModel):
    name = models.CharField(max_length=256, blank=True, verbose_name='Location')
    address = models.CharField(max_length=256, blank=True)
    zip_code = models.CharField(max_length=5, blank=True)
    city = models.CharField(max_length=64, blank=True)
    coordinates = gis_models.PointField(null=True, blank=True, srid=COORDINATE_SYSTEM_ID)
    municipality = models.ForeignKey(Municipality, null=True, blank=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

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
    name = models.CharField(max_length=256, verbose_name='Organizer')
    municipality = models.ForeignKey(Municipality, null=True, blank=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class HobbyCategory(MPTTModel, ExternalDataModel, TimestampedModel):
    name = models.CharField(max_length=256, verbose_name='Hobby Category')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    cover_image = models.ImageField(upload_to='hobbycategory_images', null=True, blank=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = 'Hobby categories'

    def __str__(self):
        return self.name


class HobbyAudience(MPTTModel, ExternalDataModel):
    name = models.CharField(max_length=256, verbose_name='Hobby Audience')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = 'Hobby Audience'

    def __str__(self):
        return self.name


class HobbyQuerySet(DistanceMixin, models.QuerySet):
    coordinates_field = 'location__coordinates'


class Hobby(ExternalDataModel, TimestampedModel):
    TYPE_FREE = 'free'
    TYPE_PAID = 'paid'  # for the cases when the recurrence of payment is not defined
    TYPE_ANNUAL = 'annual'
    TYPE_SEASONAL = 'seasonal'
    TYPE_ONE_TIME = 'one_time'

    PRICE_TYPE_CHOICES = (
        (TYPE_FREE, _('Free')),
        (TYPE_ANNUAL, _('Annual')),
        (TYPE_SEASONAL, _('Seasonal')),
        (TYPE_ONE_TIME, _('One time')),
        (TYPE_PAID, _('Paid')),
    )

    name = models.CharField(max_length=1024, verbose_name='Hobby')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    cover_image = models.ImageField(upload_to='hobby_images', null=True, blank=True)
    cover_image_modified_at = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True)
    organizer = models.ForeignKey(Organizer, null=True, blank=True, on_delete=models.CASCADE)
    municipality = models.ForeignKey(Municipality, null=True, blank=True, on_delete=models.CASCADE)
    categories = models.ManyToManyField(HobbyCategory, blank=True, related_name='hobbies', verbose_name=_('Categories'))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    price_type = models.CharField(max_length=1024, choices=PRICE_TYPE_CHOICES, default=TYPE_FREE,
                                  verbose_name='Price type')
    price_amount = models.DecimalField(max_digits=5, decimal_places=2, default=0, blank=True)
    next_event = models.OneToOneField('HobbyEvent', on_delete=models.SET_NULL, null=True, blank=True,
                                      verbose_name=_('Next event'), related_name='hobby_via_next_event')

    objects = HobbyQuerySet.as_manager()

    class Meta:
        ordering = ('id',)
        verbose_name_plural = 'Hobbies'
        get_latest_by = 'created_at'

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.price_type == self.TYPE_FREE and self.price_amount != 0:
            raise ValidationError('Price amount has to be 0 if price type is free')
        if self.price_type not in [self.TYPE_FREE, self.TYPE_PAID] and self.price_amount == 0:
            raise ValidationError('Price amount can not be 0 if price type is something else than free or paid')
        if self.price_amount < 0:
            raise ValidationError('Price amount can not be negative')

    def update_next_event(self):
        try:
            next_event = self.events.filter(
                end_date__gte=datetime.date.today()
            ).earliest('start_date')
        except HobbyEvent.DoesNotExist:
            next_event = None

        self.next_event = next_event
        self.save()

@receiver(post_delete, sender=Hobby)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.cover_image:
        if os.path.isfile(instance.cover_image.path):
            os.remove(instance.cover_image.path)

@receiver(pre_save, sender=Hobby)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        hobby = Hobby.objects.get(pk=instance.pk)
    except Hobby.DoesNotExist:
        return False

    if hobby.cover_image:
        new_file = instance.cover_image
        if not hobby.cover_image == new_file:
            if os.path.isfile(hobby.cover_image.path):
                os.remove(hobby.cover_image.path)

class HobbyEventQuerySet(DistanceMixin, models.QuerySet):
    coordinates_field = 'hobby__location__coordinates'


class PromotionQuerySet(DistanceMixin, models.QuerySet):
    coordinates_field = 'location__coordinates'


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

    recurrence_start_event = models.ForeignKey("HobbyEvent", blank=True, null=True, on_delete=models.SET_NULL,
                                               verbose_name=_('Recurrence start event'))

    objects = HobbyEventQuerySet.as_manager()

    class Meta:
        ordering = ('start_date', 'start_time')
        verbose_name = 'Hobby Event'

    def save(self, *args, **kwargs):
        # precalculate ISO 8601 day of week for cheaper querying
        self.start_weekday = self.start_date.isoweekday()
        return super().save(*args, **kwargs)

    def create_recurrency(self, recurrency_count=0):
        count = 0
        delta = datetime.timedelta(days=7)
        recurrence_date = self.start_date
        created_events = []
        while count < recurrency_count:
            count += 1
            event = copy(self)
            event.pk = None
            event.recurrence_start_event = self
            event.start_date += delta * count
            event.end_date += delta * count
            recurrence_date = event.start_date
            event.save()
            created_events.append(event)
        return created_events

    def __str__(self):
        if hasattr(self, 'hobby'):
            if self.start_date != self.end_date:
                return f'{self.hobby.name} {self.start_date} - {self.end_date}'
            else:
                return f'{self.hobby.name} {self.start_date}'
        else:
            return f'Orphan HobbyEvent with no Hobby'


class Promotion(TimestampedModel):
    """
    Promotion is an offer to users from service providers,
    for example -30% discount on sneakers.
    """
    name = models.CharField(max_length=1024)
    description = models.TextField()
    start_date = models.DateField(blank=False, null=False, verbose_name=_('Start date'))
    start_time = models.TimeField(blank=False, null=False, verbose_name=_('Start time'))
    end_date = models.DateField(blank=False, null=False, verbose_name=_('End date'))
    end_time = models.TimeField(blank=False, null=False, verbose_name=_('End time'))
    cover_image = models.ImageField(upload_to='promo_images', null=True, blank=True)
    municipality = models.ForeignKey(Municipality, null=True, blank=True, on_delete=models.CASCADE)
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE)
    available_count = models.PositiveIntegerField()
    used_count = models.PositiveIntegerField(default=0)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    objects = PromotionQuerySet.as_manager()

    def __str__(self):
        return self.name


class Benefit(TimestampedModel):
    """
    Benefit represents a single use of a Promotion, and serves as a log entry.
    """
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE)

    def clean(self):
        promotion = Promotion.objects.get(pk=self.promotion.pk)
        if promotion.used_count >= promotion.available_count:
            raise ValidationError('All available promotions have been used')

    def save(self, *args, **kwargs):
        Promotion.objects.filter(pk=self.promotion.pk).update(used_count=F('used_count') + 1)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.created_at)
