# -*- coding: utf-8 -*-
import time
import logging
import requests
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from harrastuspassi import settings
from harrastuspassi.models import Hobby, Location


LOG = logging.getLogger(__name__)
REQUESTS_TIMEOUT = 15


class Command(BaseCommand):
    help = 'Import data from Lipas'
    source = 'lipas'

    def add_arguments(self, parser):
        parser.add_argument('--url', action='store', dest='url', default=settings.LIPAS_URL,
                            help='Import from a given URL')

    def handle(self, *args, **options):
        sports_place_list = []
        page_number = 1
        created_hobbies = 0
        updated_hobbies = 0
        created_locations = 0
        updated_locations = 0

        self.stdout.write(f'Starting to pull data from {options["url"]}')
        start_time = time.time()
        with requests.Session() as session, transaction.atomic():
            session.headers.update({'Accept': 'application/json'})
            self.session = session

            while True:
                response = self.session.get(
                    options['url']
                    + f'?fields=type.name&fields=name&fields=freeUse&fields=location.city.name&fields=location.postalCode&fields=location.postalOffice&fields=location.coordinates.wgs84&fields=location.address&page={page_number}',
                    timeout=REQUESTS_TIMEOUT
                )
                has_results = response.text != '[]'
                if not has_results:
                    break
                response.raise_for_status()
                response_json = response.json()
                for sports_place in response_json:
                    zip_code_is_valid = 'postalCode' in sports_place['location'] and len(sports_place['location']['postalCode'].strip()) == 5
                    is_free = 'freeUse' in sports_place and sports_place['freeUse']

                    if 'coordinates' in sports_place['location']:
                        name = sports_place['name']
                        self.stdout.write(f'Handling hobby: {name}')
                        if zip_code_is_valid and is_free:

                            location, location_created = Location.objects.update_or_create(
                                data_source=self.source,
                                name=sports_place.get('name'),
                                address=sports_place['location'].get('address', ''),
                                zip_code=sports_place['location'].get('postalCode', '').strip(),
                                city=sports_place['location']['city'].get('name'),
                                coordinates=Point(
                                    sports_place['location']['coordinates']['wgs84'].get('lon', ''),
                                    sports_place['location']['coordinates']['wgs84'].get('lat', '')
                                )
                            )

                            if location_created:
                                created_locations += 1
                            else:
                                updated_locations += 1

                            hobby, hobby_created = Hobby.objects.update_or_create(
                                data_source=self.source,
                                name=sports_place['name'],
                                price_type=Hobby.TYPE_FREE,
                                location=location
                            )

                            if hobby_created:
                                created_hobbies += 1
                            else:
                                updated_hobbies += 1
                page_number += 1
            execution_time = round(time.time() - start_time, 2)
            self.stdout.write(f'\n{created_hobbies} new hobbies, {updated_hobbies} updated hobbies, {created_hobbies} new locations, {updated_hobbies} updated locations in {execution_time} seconds')