# -*- coding: utf-8 -*-
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.db import models
from rest_framework.exceptions import APIException

from harrastuspassi.geocoding import get_coordinates_from_address
from harrastuspassi.models import Location


class Command(BaseCommand):
    help = 'Geocode location objects with (0, 0) or Null coordinates'

    def handle(self, *args, **options):
        faulty_coordinates = models.Q(coordinates=Point(0, 0)) | models.Q(coordinates__isnull=True)
        # We implicitly exclude faulty locations that are imported, because those should not be edited in our database
        locations_with_faulty_coordinates = Location.objects.filter(faulty_coordinates).filter(data_source='')
        self.stdout.write(
            f'Found {locations_with_faulty_coordinates.count()} locations with faulty or null coordinates.'
        )

        for location in locations_with_faulty_coordinates:
            formatted_address = f'{location.address},+{location.zip_code}+{location.city}'
            self.stdout.write(f'Getting coordinates for address {repr(formatted_address)}')
            try:
                location.coordinates = get_coordinates_from_address(formatted_address)
                location.save()
            except APIException:
                self.stdout.write(f'Could not get coordinates for {repr(location)}')
