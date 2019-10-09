# -*- coding: utf-8 -*-

import logging
import re
import requests
from collections import namedtuple
from django.core.management.base import BaseCommand
from django.db import transaction
from typing import Dict, Iterator, List
from harrastuspassi import settings
from harrastuspassi.models import Hobby


LOG = logging.getLogger(__name__)
REQUESTS_TIMEOUT = 15

Keyword = namedtuple('Keyword', ['source', 'id'])


class InvalidKeywordException(Exception):
    pass


class Command(BaseCommand):
    help = "Import data from Linked Courses"

    def add_arguments(self, parser):
        parser.add_argument('--url', action='store', dest='url', default=settings.LINKED_COURSES_URL,
                            help='Import from a given URL')

    def handle(self, *args, **options):
        import pprint
        for page in self.get_event_pages(options['url']):
            for event in page:
                # pprint.pprint(json.dumps(event, indent=4))
                pprint.pprint(self.get_keywords(event))

    def get_event_pages(self, events_url: str) -> Iterator[List[Dict]]:
        next_url = events_url
        with requests.Session() as session:
            session.headers.update({'Accept': 'application/json'})
            while next_url:
                response = session.get(next_url, timeout=REQUESTS_TIMEOUT)
                response.raise_for_status()
                response_json = response.json()
                data = response_json.get('data', [])
                meta = response_json.get('meta', {})
                next_url = meta.get('next', None)
                yield data

    def upsert_hobby(self, event: Dict) -> Hobby:
        """ Create or update existing Hobby based on event.
            Hobby will only be created if it's keywords match some of our categories.
        """
        # first verify that keywords match categories. compare category source + id to keyword source + id
        # if so, find existing hobby, update data and hobbyevents
        # or create new
        # TODO: HOW TO ACTUALLY PARSE HOBBY + HOBBYEVENTS FROM THE MASS OF EVENTS?
        return Hobby()

    def get_keywords(self, event: Dict) -> List[Keyword]:
        """ Get all keywords of an event """
        keywords = []
        for keyword in event.get('keywords', []):
            try:
                keywords.append(self.parse_ld_keyword_id(keyword['@id']))
            except InvalidKeywordException:
                self.stderr.write(f'Can not parse keyword: {repr(keyword)}')
        return keywords

    def parse_ld_keyword_id(self, ld_keyword_id: str) -> Keyword:
        """ Parse keyword source and id from the id url. Avoid a roundtrip to the
            API for getting the actual Keyword object.
        """
        match = re.match('https?://.*/linkedcourses/.*/keyword/(.*):(.*)/', ld_keyword_id)
        if match is None:
            raise InvalidKeywordException
        return Keyword(source=match.group(1), id=match.group(2))

