
# -*- coding: utf-8 -*-
#
# Copyright Haltu Oy, info@haltu.fi
# All rights reserved.
#

import logging
from django.db import models

LOG = logging.getLogger(__name__)


class Location(models.Model):
  name = models.CharField(max_length=256)

  def __str__(self):
    return self.name


class Hobby(models.Model):
  DAY_OF_WEEK_CHOICES = [
    (1, 'Maanantai'),
    (2, 'Tiistai'),
    (3, 'Keskiviikko'),
    (4, 'Torstai'),
    (5, 'Perjantai'),
    (6, 'Lauantai'),
    (7, 'Sunnuntai'),
  ]

  name = models.CharField(max_length=256)
  day_of_week = models.IntegerField(choices=DAY_OF_WEEK_CHOICES, null=True, blank=True)
  location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
  image = models.ImageField(upload_to='hobby_images', null=True, blank=True)

  def __str__(self):
    return self.name

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2
