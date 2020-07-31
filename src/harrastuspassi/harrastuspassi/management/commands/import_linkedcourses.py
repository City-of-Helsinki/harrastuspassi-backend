# -*- coding: utf-8 -*-

"""
Create Hobbies and HobbyEvents from data in Linked Courses

TODO: using the full URI ('@id' attribute) as origin_id is not a good idea. should
use the real id instead, but this requires either parsing from the URI or doing an
API request every time
TODO: organizer is not saved for the Hobbies
TODO: multiple objects with same data_source and origin_id are not handled correctly and will crash
TODO: handle only recently changed or created events by querying modified_by
"""
import iso8601
import json
import logging
import operator
import os
import re
import requests
from collections import namedtuple
from django.core.files import File
from functools import lru_cache, reduce
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from tempfile import NamedTemporaryFile
from typing import Dict, Iterator, List, Optional, Set, Tuple, Union
from urllib.parse import urlparse
from harrastuspassi import settings
from harrastuspassi.models import (Hobby,
                                   HobbyAudience,
                                   HobbyCategory,
                                   HobbyEvent,
                                   Location,
                                   Organizer)


LOG = logging.getLogger(__name__)
REQUESTS_TIMEOUT = 15
# Most of the events in linkedcourses are using keywords from
# https://api.hel.fi/linkedevents/v1/keyword_set/helsinki:audiences/?include=keywords to define
# the event audience

INCLUDE_AUDIENCE_NAMES = ['Opiskelijat', 'Nuoret']
EXCLUDE_AUDIENCE_NAMES = ['Koululaiset', 'Lapset', 'Lapsiperheet', 'Vauvaperheet']

# Keywords in Linked Courses come from several ontologies.
# We are interested mainly in YSO ontology.
# Keyword source is the name of the ontology and id is the identifier in that ontology.
Keyword = namedtuple('Keyword', ['source', 'id'])


class InvalidKeywordException(Exception):
    pass


class Command(BaseCommand):
    help = 'Import data from Linked Courses'
    source = 'linked_courses'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.INCLUDE_AUDIENCE = self.populate_keyword_set(INCLUDE_AUDIENCE_NAMES, 'Include Audience')
        self.EXCLUDE_AUDIENCE = self.populate_keyword_set(EXCLUDE_AUDIENCE_NAMES, 'Exclude Audience')

    def populate_keyword_set(self, keyword_names: List, keyword_type: str, parent: str = '') -> Set[Keyword]:
        """Stores ids for the audience keywords in order to save on DB queries."""
        qs = HobbyAudience.objects.all()
        if parent:
            qs = qs.get(name=parent).get_children()
        keyword_qs = qs.filter(name__in=keyword_names).values('data_source', 'origin_id')
        if len(keyword_qs) < len(keyword_names):
            self.stderr.write(f'Some of the keywords from {keyword_type} do not match the categories.')
        keyword_set = set([Keyword(source=i['data_source'], id=i['origin_id']) for i in keyword_qs])
        return keyword_set

    def add_arguments(self, parser):
        parser.add_argument('--url', action='store', dest='url', default=settings.LINKED_COURSES_URL,
                            help='Import from a given URL')

    def handle(self, *args, **options):
        self.stdout.write(f'Starting to pull events from {options["url"]}\n')
        found_hobby_origin_ids = []
        found_hobbyevent_origin_ids = []
        orphaned_hobby_events = []
        with requests.Session() as session, transaction.atomic():
            session.headers.update({'Accept': 'application/json'})
            self.session = session
            for page in self.get_event_pages(options['url']):
                for event in page:
                    objects = self.handle_event(event)
                    for obj in objects:
                        if isinstance(obj, HobbyEvent) and not hasattr(obj, 'hobby'):
                            # we might have created HobbyEvents which could not determine
                            # a Hobby instance. these are not yet persisted to db.
                            orphaned_hobby_events.append(obj)
                        if isinstance(obj, Hobby):
                            found_hobby_origin_ids.append(obj.origin_id)
                        elif isinstance(obj, HobbyEvent):
                            found_hobbyevent_origin_ids.append(obj.origin_id)
        # try to find hobbies for orphaned events now that we have processed all pages
        self.handle_orphaned_hobby_events(orphaned_hobby_events)
        self.handle_deletions(found_hobby_origin_ids, found_hobbyevent_origin_ids)
        self.stdout.write(f'Finished.\n')

    def get_event_pages(self, events_url: str) -> Iterator[List[Dict]]:
        next_url = events_url
        while next_url:
            response = self.session.get(next_url, timeout=REQUESTS_TIMEOUT)
            response.raise_for_status()
            response_json = response.json()
            data = response_json.get('data', [])
            meta = response_json.get('meta', {})
            next_url = meta.get('next', None)
            yield data

    def handle_event(self, event: Dict) -> List[Union[Hobby, HobbyEvent]]:
        """ Handle one event. Can return an empty list, one object or many objects
            generated from the event.
        """
        # if the age is not over 13 - skip event
        event_keywords = self.get_keywords(event)
        if not self.check_age(event, event_keywords):
            return []

        # verify that keywords match categories. compare category source + id to keyword source + id
        categories_for_event = self.determine_categories(event_keywords)
        if len(categories_for_event) == 0:
            # This event does not map to any category we are interested in. Skip it.
            return []

        result_objects = []
        # is this a Hobby or a HobbyEvent?
        if self.is_hobby(event):
            result_objects.append(self.handle_hobby(event, categories_for_event))
        if self.is_hobby_event(event):
            result_objects.append(self.handle_hobby_event(event))
        return result_objects

    def check_age(self, event: Dict, event_keywords: Set[Keyword]) -> bool:
        if event.get('audience_min_age'):
            if event['audience_min_age'] > 12:
                return True
            else:
                self.stdout.write(f"audience_min_age for {event.get('name')} is {event['audience_min_age']}, skipping.")
                return False
        if event_keywords.intersection(self.INCLUDE_AUDIENCE):
            if event_keywords.intersection(self.EXCLUDE_AUDIENCE):
                msg = f"{event.get('name')} is also for {event_keywords.intersection(self.EXCLUDE_AUDIENCE)}, skipping."
                self.stdout.write(msg)
                return False
            else:
                return True
        else:
            self.stdout.write(f"{event.get('name')} no audience_min_age and suitable audience keywords. Skipping.")
            return False

    def handle_hobby(self, event: Dict, categories: List[HobbyCategory]) -> Hobby:
        """ Handle an event, creating or updating existing Hobby """
        data = {
            'name': event['name'].get('fi'),  # TODO language support
            'location': self.get_location(event),
            'description': self.get_description(event),
            'organizer': self.get_organizer(event),
        }
        hobby, created = Hobby.objects.get_or_create(data_source=self.source, origin_id=event['@id'], defaults=data)
        if not created:
            self.stdout.write(f'Updating Hobby {hobby.pk} {hobby.name}\n')
            is_dirty = False
            for field, value in data.items():
                if getattr(hobby, field) != value:
                    is_dirty = True
                    setattr(hobby, field, value)
            if is_dirty:
                hobby.save()
        else:
            self.stdout.write(f'Created Hobby {hobby.pk} {hobby.name}\n')
        hobby.categories.set(categories)
        self.handle_hobby_cover_image(event, hobby)
        return hobby

    def handle_hobby_cover_image(self, event: Dict, hobby: Hobby) -> None:
        if not event['images']:
            return
        event_image_modified_at = iso8601.parse_date(event['images'][0]['last_modified_time'])
        is_event_image_modified = hobby.cover_image_modified_at < event_image_modified_at
        should_fetch_new_image = is_event_image_modified or not hobby.cover_image
        if not should_fetch_new_image:
            return
        image_file, image_name = self.fetch_image(event)
        if not image_file:
            return
        hobby.cover_image.save(f'hobby_{hobby.pk}_{image_name}', image_file)
        hobby.cover_image_modified_at = event_image_modified_at
        hobby.save()

    def handle_hobby_event(self, event: Dict) -> Optional[HobbyEvent]:
        """ Handle an event, creating or updating existing HobbyEvent """
        try:
            event_start_dt = iso8601.parse_date(event['start_time'])
            event_end_dt = iso8601.parse_date(event['end_time'])
        except iso8601.ParseError:
            self.stderr.write(f'Can not parse start or end time of event {event["id"]}')
            return None
        if event['super_event']:
            hobby_origin_id = event['super_event']
        else:
            # this is a self-contained event which produces both hobby and hobbyevent
            hobby_origin_id = event['@id']
        try:
            hobby = Hobby.objects.get(data_source=self.source, origin_id=hobby_origin_id)
        except Hobby.DoesNotExist:
            hobby = None
        data = {
            'hobby': hobby,
            'start_date': event_start_dt.date(),
            'start_time': event_start_dt.time(),
            'end_date': event_end_dt.date(),
            'end_time': event_end_dt.time(),
        }
        if hobby is None:
            # we have no Hobby for this HobbyEvent (yet)
            if HobbyEvent.objects.filter(data_source=self.source, origin_id=event['@id']):
                # We have previously had this event but it's super_event has changed??
                # TODO: handle this better. now just bail out...
                self.stderr.write(
                    f'I don\'t know how to handle an event which had '
                    f'it\'s super_event changed, sorry. Event @id: {event["@id"]}'
                )
                return None
            # instantiate the object but do not persist yet. we may have a
            # hobby at the end of the run.
            self.stdout.write(f'Created a HobbyEvent but we don\'t have a Hobby for it. Reprocessing later.\n')
            orphan_event = HobbyEvent(data_source=self.source, origin_id=event['@id'], **data)
            setattr(orphan_event, '_hobby_origin_id', hobby_origin_id)
            return orphan_event
        hobby_event, created = HobbyEvent.objects.get_or_create(
            data_source=self.source, origin_id=event['@id'], defaults=data)
        if not created:
            self.stdout.write(f'Updating HobbyEvent {hobby_event.pk} {str(hobby_event)}\n')
            is_dirty = False
            for field, value in data.items():
                if getattr(hobby_event, field) != value:
                    is_dirty = True
                    setattr(hobby_event, field, value)
            if is_dirty:
                hobby_event.save()
        else:
            self.stdout.write(f'Created HobbyEvent {hobby_event.pk} {str(hobby_event)}\n')
        return hobby_event

    def handle_orphaned_hobby_events(self, hobby_events: List[HobbyEvent]) -> None:
        if hobby_events:
            self.stdout.write(f'Starting to handle orphaned HobbyEvents\n')
        for hobby_event in hobby_events:
            hobby_origin_id = getattr(hobby_event, '_hobby_origin_id', None)
            if not hobby_origin_id:
                self.stderr.write(f'Orphan event {hobby_event.origin_id} is missing hobby origin id, skipping.')
                continue
            try:
                hobby = Hobby.objects.get(data_source=self.source, origin_id=hobby_origin_id)
                hobby_event.hobby = hobby
                hobby_event.save()
                self.stdout.write(f'Created HobbyEvent {hobby_event.pk} {str(hobby_event)}\n')
            except Hobby.DoesNotExist:
                self.stderr.write(
                    f'Orphan event {hobby_event.origin_id} ignored - '
                    f'we don\'t have a hobby with origin_id {hobby_origin_id}\n')
                continue
            except Hobby.MultipleObjectsReturned:
                self.stderr.write(
                    f'Orphan event {hobby_event.origin_id} ignored - '
                    f'multiple hobbies with origin_id {hobby_origin_id} found\n')
                continue

    def handle_deletions(
            self,
            found_hobby_origin_ids: List[str],
            found_hobbyevent_origin_ids: List[str]
        ) -> None:
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

    def determine_categories(self, event_keywords: Set[Keyword]) -> List[HobbyCategory]:
        """ Get a list of Category objects an event maps to based on its keywords """
        filters = [Q(data_source=kw.source, origin_id=kw.id) for kw in event_keywords]
        return list(HobbyCategory.objects.filter(reduce(operator.or_, filters)))

    def get_keywords(self, event: Dict) -> Set[Keyword]:
        """ Get all keywords of an event """
        keywords = []
        for keyword in event.get('keywords', []):
            try:
                keywords.append(self.parse_ld_keyword_id(keyword['@id']))
            except InvalidKeywordException:
                self.stderr.write(f'Can not parse keyword: {repr(keyword)}\n')
        return set(keywords)

    def parse_ld_keyword_id(self, ld_keyword_id: str) -> Keyword:
        """ Parse keyword source and id from the id url. Avoid a roundtrip to the
            API for getting the actual Keyword object.
        """
        match = re.match('https?://.*/linkedcourses/.*/keyword/(.*):(.*)/', ld_keyword_id)
        if match is None:
            raise InvalidKeywordException
        return Keyword(source=match.group(1), id=match.group(2))

    def is_hobby(self, event: Dict) -> bool:
        """ Event should form a Hobby if:
            - super_event == null && super_event_type == null
            - super_event_type == recurring
        """
        is_self_contained_event = event['super_event'] is None and event['super_event_type'] is None
        is_recurring_superevent = event['super_event_type'] == 'recurring'
        return is_self_contained_event or is_recurring_superevent

    def is_hobby_event(self, event: Dict) -> bool:
        """ Event should form a HobbyEvent if:
            - super_event == null && super_event_type == null
            - super_event != null && super_event_type == null
        """
        is_self_contained_event = event['super_event'] is None and event['super_event_type'] is None
        is_plain_subevent = event['super_event'] is not None and event['super_event_type'] is None
        return is_self_contained_event or is_plain_subevent

    def get_location(self, event: Dict) -> Optional[Location]:
        location_url = event['location'].get('@id')
        if location_url is None:
            return None
        location_data = self.fetch_location_data(location_url)
        if location_data is None:
            return None
        data = {
            'name': location_data['name'].get('fi'),  # TODO: language support
            #  not using plain location_data.get('postal_code', '') to avoid None values if
            #  location_data['postal__code'] == None
            'zip_code': location_data.get('postal_code') if location_data.get('postal_code') else '',
            'coordinates': None
        }
        if location_data['address_locality']:
            data['city'] = location_data['address_locality'].get('fi', '')
        if location_data['street_address']:
            data['address'] = location_data['street_address'].get('fi', '')

        if location_data['position'] and location_data['position'].get('type') == 'Point':
            # Are these the right way?
            lon = location_data['position']['coordinates'][0]
            lat = location_data['position']['coordinates'][1]
            data['coordinates'] = Point(x=lon, y=lat)
        location, created = Location.objects.get_or_create(
            data_source=self.source,
            origin_id=location_data['@id'],
            defaults=data)
        if not created:
            is_dirty = False
            for field, value in data.items():
                if getattr(location, field) != value:
                    is_dirty = True
                    setattr(location, field, value)
            if is_dirty:
                location.save()
        return location

    @lru_cache()
    def fetch_location_data(self, url: str) -> Optional[Dict]:
        """ Get data for a specific location from Linked Courses API.
            Results are memoized with lru_cache to avoid multiple roundtrips to
            the same resource endpoint during one execution run.
        """
        try:
            response = self.session.get(url, timeout=REQUESTS_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.stderr.write(f'Could not get location data: {str(e)}\n')
            return None
        except (json.decoder.JSONDecodeError, TypeError) as e:
            self.stderr.write(f'Could not parse location data: {str(e)}\n')
            return None

    def fetch_image(self, event: Dict) -> Tuple[Optional[File], Optional[str]]:
        """ Get a File instance with a downloaded image file.
            Returns the first image in the event if it's accessible.
        """
        temp_file = NamedTemporaryFile(delete=True)
        if len(event['images']) == 0:
            return (None, None)
        image_url = event['images'][0]['url']
        image_name = self.parse_image_name(event['images'][0]['url'])
        if not image_url or not image_name:
            return (None, None)
        try:
            response = self.session.get(image_url, timeout=REQUESTS_TIMEOUT)
            response.raise_for_status()
            temp_file.write(response.content)
            temp_file.flush()
            return (File(temp_file), image_name)
        except requests.exceptions.RequestException as e:
            self.stderr.write(f'Could not get image data: {str(e)}\n')
            return (None, None)
        except IOError as e:
            self.stderr.write(f'Could not save image file: {str(e)}\n')
            return (None, None)

    def parse_image_name(self, url: str) -> Optional[str]:
        """ Get filename from image url """
        parsed = urlparse(url)
        return os.path.basename(parsed.path)

    def get_description(self, event: Dict) -> str:
        short_description = event.get('short_description')
        if short_description is None:
            return ''
        return short_description.get('fi')  # TODO: language support

    def get_organizer(self, event: Dict) -> Organizer:
        # TODO: there is currently no organizer data in Linked Courses. return Helsinki here?
        return None
