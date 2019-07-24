
# -*- coding: utf-8 -*-
import logging
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.gis.db import models as gis_models
from django.core.exceptions import ValidationError

LOG = logging.getLogger(__name__)


class TimestampedModel(models.Model):
  created_at = models.DateTimeField(editable=False, default=timezone.now)
  updated_at = models.DateTimeField(editable=False)

  class Meta:
    abstract = True

  def save(self, *args, **kwargs):
    self.updated_at = timezone.now()
    return super().save(*args, **kwargs)


class Location(TimestampedModel):
  name = models.CharField(max_length=256, blank=True)
  address = models.CharField(max_length=256, blank=True)
  zip_code = models.CharField(max_length=5, blank=True)
  city = models.CharField(max_length=64, blank=True)
  coordinates = gis_models.PointField(null=True, blank=True)

  def lat(self):
    return self.coordinates.y if self.coordinates else None

  def lon(self):
    return self.coordinates.x if self.coordinates else None

  def __str__(self):
    return self.name

  def clean(self):
    super(Location, self).clean()

    if not self.name and not self.city and not self.coordinates:
      raise ValidationError('One of the following fields is required: name, city or coordinates')


class Organizer(TimestampedModel):
  name = models.CharField(max_length=256)

  def __str__(self):
    return self.name


class HobbyCategory(MPTTModel):
  name = models.CharField(max_length=256, unique=True)
  parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

  class MPTTMeta:
    order_insertion_by = ['name']

  def __str__(self):
    return self.name


class Hobby(models.Model):
  DAY_OF_WEEK_CHOICES = [
    (1, _('Monday')),
    (2, _('Tuesday')),
    (3, _('Wednesday')),
    (4, _('Thursday')),
    (5, _('Friday')),
    (6, _('Saturday')),
    (7, _('Sunday')),
  ]

  name = models.CharField(max_length=256)
  start_day_of_week = models.IntegerField(choices=DAY_OF_WEEK_CHOICES, null=True, blank=True)
  end_day_of_week = models.IntegerField(choices=DAY_OF_WEEK_CHOICES, null=True, blank=True)
  location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
  cover_image = models.ImageField(upload_to='hobby_images', null=True, blank=True)
  description = models.TextField(blank=True)
  organizer = models.ForeignKey(Organizer, null=True, blank=True, on_delete=models.CASCADE)
  category = models.ForeignKey(HobbyCategory, null=True, blank=True, on_delete=models.CASCADE)

  def __str__(self):
    return self.name

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2
