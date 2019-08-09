
# -*- coding: utf-8 -*-
import logging
from django.contrib.gis.db import models as gis_models
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

LOG = logging.getLogger(__name__)


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(editable=False, default=timezone.now)
    updated_at = models.DateTimeField(editable=False, auto_now=True)

    class Meta:
        abstract = True


class Location(TimestampedModel):
    name = models.CharField(max_length=256, blank=True)
    address = models.CharField(max_length=256, blank=True)
    zip_code = models.CharField(max_length=5, blank=True)
    city = models.CharField(max_length=64, blank=True)
    coordinates = gis_models.PointField(null=True, blank=True)

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


class Organizer(TimestampedModel):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class HobbyCategory(MPTTModel, TimestampedModel):
    name = models.CharField(max_length=256, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = 'Hobby categories'

    def __str__(self):
        return self.name


class Hobby(TimestampedModel):
    name = models.CharField(max_length=1024)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    cover_image = models.ImageField(upload_to='hobby_images', null=True, blank=True)
    description = models.TextField(blank=True)
    organizer = models.ForeignKey(Organizer, null=True, blank=True, on_delete=models.CASCADE)
    category = models.ForeignKey(HobbyCategory, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Hobbies'

    def __str__(self):
        return self.name


class HobbyEvent(TimestampedModel):
    """ An event in time when a hobby takes place """
    hobby = models.ForeignKey(Hobby, related_name='events', verbose_name=_('Hobby'),
                              null=False, on_delete=models.CASCADE)
    start_date = models.DateField(blank=False, null=False, verbose_name=_('Start date'))
    start_time = models.TimeField(blank=False, null=False, verbose_name=_('Start time'))
    end_date = models.DateField(blank=False, null=False, verbose_name=_('End date'))
    end_time = models.TimeField(blank=False, null=False, verbose_name=_('End time'))

    class Meta:
        ordering = ('start_date', 'start_time')
        verbose_name = 'Hobby Event'

    def __str__(self):
        if self.start_date != self.end_date:
            return f'{self.hobby.name} {self.start_date} - {self.end_date}'
        else:
            return f'{self.hobby.name} {self.start_date}'
