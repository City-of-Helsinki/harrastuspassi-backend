# -*- coding: utf-8 -*-
import datetime
import time
import logging
import requests
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.db import transaction
from harrastuspassi import settings
from harrastuspassi.models import Hobby, HobbyCategory, HobbyEvent, Location

LOG = logging.getLogger(__name__)
REQUESTS_TIMEOUT = 15


class Command(BaseCommand):
    help = 'Import data from Lipas'
    source = 'lipas'

    category_mappings = {
        1180: 'Frisbeegolf',
        4401: 'Kävely',
        4403: 'Kävely',
        4402: 'Hiihto',
        1520: 'Luistelu',
        4404: 'Retkeily',
        4421: 'Moottoriurheilu',
        4422: 'Moottoriurheilu',
        4412: 'Pyöräily',
        4405: 'Retkeily',
        3230: 'Uinti',
        3130: 'Uinti',
        3210: 'Uinti',
        3220: 'Uinti',
        3110: 'Uinti',
        1130: 'Kuntosalit',
        4452: 'Melonta',
        1210: 'Yleisurheilu',
        2290: 'Petankki',
        4210: 'Talviurheilu',
        4230: 'Talviurheilu',
        4240: 'Talviurheilu',
        4220: 'Hiihto',
        4310: 'Mäkihyppy',
        1140: 'Parkour',
        101: 'Retkeily',
        103: 'Retkeily',
        104: 'Retkeily',
        2280: 'Tennis',
        1360: 'Pesäpallo',
        2150: 'Urheilu ja liikunta',
        108: 'Retkeily',
        107: 'Retkeily',
        106: 'Retkeily',
        112: 'Retkeily',
        204: 'Luonto ja eläimet',
        111: 'Retkeily',
        201: 'Kalastus',
        202: 'Retkeily',
        1110: 'Urheilu ja liikunta',
        2270: 'Palloilu',
        110: 'Retkeily',
        1120: 'Urheilu ja liikunta',
        2250: 'Rullalautailu',
        1150: 'Rullalautailu',
        1220: 'Yleisurheilu',
        3240: 'Uinti',
        203: 'Moottoriveneily',
        206: 'Retkeily',
        304: 'Retkeily',
        1310: 'Koripallo',
        1320: 'Lentopallo',
        1350: 'Jalkapallo',
        1370: 'Tennis',
        1380: 'Rullakiekko',
        1330: 'Lentopallo',
        1340: 'Palloilu',
        1160: 'Pyöräily',
        1170: 'Pyöräily',
        1530: 'Luistelu',
        1560: 'Luistelu',
        1620: 'Golf',
        1640: 'Golf',
        2220: 'Urheilu ja liikunta',
        301: 'Retkeily',
        2140: 'Kamppailulajit',
        2210: 'Urheilu ja liikunta',
        2240: 'Salibandy',
        2260: 'Sulkapallo',
        2120: 'Voimailu',
        1550: 'Luistelu',
        1610: 'Golf',
        1630: 'Golf',
        1510: 'Luistelu',
        2110: 'Urheilu ja liikunta',
        2130: 'Voimailu',
        2310: 'Yleisurheilu',
        2320: 'Telinevoimistelu',
        2330: 'Pöytätennis',
        2340: 'Miekkailu',
        2350: 'Tanssi',
        4110: 'Laskettelu',
        4430: 'Ratsastus',
        2230: 'Jalkapallo',
        109: 'Retkeily',
        4320: 'Hyppyrimäki',
        2370: 'Kiipeily',
        2380: 'Parkour',
        2510: 'Luistelu',
        4440: 'Hiihto',
        2530: 'Luistelu',
        3120: 'Uinti',
        2610: 'Keilailu',
        2520: 'Luistelu',
        4451: 'Melonta',
        4510: 'Suunnistus',
        4530: 'Suunnistus',
        4610: 'Ampumahiihto',
        4630: 'Hiihto',
        4710: 'Kiipeily',
        4720: 'Kiipeily',
        4840: 'Jousiammunta',
        4830: 'Jousiammunta',
        5110: 'Soutu',
        5140: 'Vesihiihto',
        4520: 'Suunnistus',
        4640: 'Hiihto',
        5120: 'Purjehdus',
        5130: 'Moottoriveneily',
        5310: 'Moottoriurheilu',
        5320: 'Moottoripyöräily',
        5330: 'Moottoriurheilu',
        6110: 'Ratsastus',
        6120: 'Ratsastus',
        6210: 'Agility',
        5340: 'Karting',
        5360: 'Autourheilu',
        6130: 'Ratsastus',
        6220: 'Agility',
        5150: 'Melonta',
        5160: 'Melonta',
        4411: 'Maastopyöräily',
        102: 'Retkeily',
        302: 'Retkeily',
        1540: 'Luistelu',
    }

    def add_arguments(self, parser):

        parser.add_argument('--url', action='store', dest='url', default=settings.LIPAS_URL,
                            help='Import from a given URL')
        parser.add_argument('--non_hp', action='store_false', dest='import_only_hp', default=True,
                            help='Import also the places that have Harrastuspassi flag set to False')

    def handle(self, *args, **options):
        page_number = 1
        created_hobbies = 0
        updated_hobbies = 0
        created_locations = 0
        updated_locations = 0
        found_hobby_origin_ids = []
        found_hobbyevent_origin_ids = []

        self.stdout.write(f'Starting to pull data from {options["url"]}')
        start_time = time.time()
        with requests.Session() as session, transaction.atomic():
            session.headers.update({'Accept': 'application/json'})
            self.session = session

            while True:
                query_params = {
                    'fields': [
                        'type.name',
                        'name',
                        'freeUse',
                        'location.city.name',
                        'location.postalCode',
                        'location.postalOffice',
                        'location.coordinates.wgs84',
                        'location.address',
                        'type.typeCode',
                        'properties'
                    ],
                    'page': page_number,
                    'harrastuspassi': 'true' if options['import_only_hp'] else 'false',
                }
                response = self.session.get(
                    options['url'],
                    timeout=REQUESTS_TIMEOUT,
                    params=query_params,
                )
                has_results = response.text != '[]'
                if not has_results:
                    break
                response.raise_for_status()
                response_json = response.json()
                for sports_place in response_json:
                    cleaned_postal_code = sports_place['location'].get('postalCode', '').strip()
                    zip_code_is_valid = len(cleaned_postal_code) == 5
                    is_free = 'freeUse' in sports_place and sports_place['freeUse']

                    if not 'coordinates' in sports_place['location']:
                        continue
                    name = sports_place.get('name')
                    type_code = sports_place['type'].get('typeCode')

                    self.stdout.write(f'Handling hobby: {name}')
                    if not zip_code_is_valid or not type_code in self.category_mappings.keys():
                        continue
                    location, location_created = Location.objects.update_or_create(
                        data_source=self.source,
                        origin_id=sports_place.get('sportsPlaceId'),
                        defaults={
                            'address': sports_place['location'].get('address', ''),
                            'city': sports_place['location']['city'].get('name'),
                            'coordinates': Point(
                                sports_place['location']['coordinates']['wgs84'].get('lon', ''),
                                sports_place['location']['coordinates']['wgs84'].get('lat', '')
                            ),
                            'name': sports_place.get('name'),
                            'zip_code': cleaned_postal_code
                        },
                    )

                    if location_created:
                        created_locations += 1
                    else:
                        updated_locations += 1

                    category, _category_created = HobbyCategory.objects.get_or_create(
                        name=self.category_mappings[type_code],
                    )
                    # Lipas import only tells us if a hobby is free, there is no price information or type available
                    if is_free:
                        price_type = Hobby.TYPE_FREE
                    else:
                        price_type = Hobby.TYPE_PAID
                    hobby, hobby_created = Hobby.objects.update_or_create(
                        data_source=self.source,
                        origin_id=sports_place.get('sportsPlaceId'),
                        defaults={
                            'location': location,
                            'name': sports_place['name'],
                            'price_type': price_type,
                            'description': sports_place['properties'].get('infoFi', ''),
                        }
                    )
                    hobby.categories.set([category])
                    found_hobby_origin_ids.append(hobby.origin_id)

                    hobbyevent, hobbyevent_created = HobbyEvent.objects.update_or_create(
                        data_source=self.source,
                        origin_id=sports_place.get('sportsPlaceId'),
                        defaults={
                            'hobby': hobby,
                            'start_date': datetime.date.today(),
                            'end_date': datetime.date.today() + datetime.timedelta(days=365),
                            'start_time': datetime.datetime.strptime('00:00', '%H:%M').time(),
                            'end_time': datetime.datetime.strptime('00:00', '%H:%M').time(),
                        }
                    )
                    found_hobbyevent_origin_ids.append(hobbyevent.origin_id)

                    if hobby_created:
                        created_hobbies += 1
                    else:
                        updated_hobbies += 1
                page_number += 1
        execution_time = round(time.time() - start_time, 2)
        self.stdout.write(f'\n{created_hobbies} new hobbies, {updated_hobbies} updated hobbies, {created_hobbies} new locations, {updated_hobbies} updated locations in {execution_time} seconds')
        self.handle_deletions(found_hobby_origin_ids, found_hobbyevent_origin_ids)

    def handle_deletions(self, found_hobby_origin_ids, found_hobbyevent_origin_ids):
        hobbyevent_qs = HobbyEvent.objects.filter(data_source=self.source)
        hobbyevents_to_delete_qs = hobbyevent_qs.exclude(origin_id__in=found_hobbyevent_origin_ids)
        hobby_qs = Hobby.objects.filter(data_source=self.source)
        hobbies_to_delete_qs = hobby_qs.exclude(origin_id__in=found_hobby_origin_ids)
        if (
            hobbyevents_to_delete_qs.count() >= hobbyevent_qs.count() or
            hobbies_to_delete_qs.count() >= hobby_qs.count()
        ):
            self.stderr.write(
                'Run would delete all Hobbies or HobbyEvents, something is wrong, skipping deletion.'
            )
            return
        self.stdout.write(f'HobbyEvents being deleted count: {hobbyevents_to_delete_qs.count()}\n')
        hobbyevents_to_delete_qs.delete()
        self.stdout.write(f'Hobbies being deleted count: {hobbies_to_delete_qs.count()}\n')
        hobbies_to_delete_qs.delete()