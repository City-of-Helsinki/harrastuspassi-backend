
# -*- coding: utf-8 -*-
import logging
from django.db import models
from django.utils.translation import gettext_lazy as _

LOG = logging.getLogger(__name__)


class Location(models.Model):
  name = models.CharField(max_length=256)

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
  day_of_week = models.IntegerField(choices=DAY_OF_WEEK_CHOICES, null=True, blank=True)
  location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
  cover_image = models.ImageField(upload_to='hobby_images', null=True, blank=True)

  def __str__(self):
    return self.name

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2
