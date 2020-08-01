import datetime
import pytest


@pytest.fixture
def event_with_images_only(frozen_datetime):
    return {
        'images': [
            {
                '@context': 'http://schema.org',
                '@id': 'foo',
                '@type': 'ImageObject',
                'alt_text': None,
                'created_time': (frozen_datetime - datetime.timedelta(days=6 * 30)).isoformat() + 'Z',
                'cropping': '',
                'data_source': 'foo',
                'id': 1,
                'last_modified_time': (frozen_datetime - datetime.timedelta(days=30)).isoformat() + 'Z',
                'license': 'cc_by',
                'name': '',
                'photographer_name': None,
                'publisher': 'foo:u1',
                'url': 'https://doesnotexist.local/images/image001.jpg'
            }
        ],
    }


@pytest.fixture
def imported_hobby(hobby_with_events):
    hobby_with_events.data_source = 'linked_courses'
    hobby_with_events.origin_id = 'foo:1'
    hobby_with_events.save()
    event = hobby_with_events.events.all()[0]
    event.data_source = 'linked_courses'
    event.origin_id = 'foo:1'
    event.save()
    event = hobby_with_events.events.all()[1]
    event.data_source = 'linked_courses'
    event.origin_id = 'foo:2'
    event.save()
    return hobby_with_events


@pytest.fixture
def imported_hobby2(hobby_with_events2):
    hobby_with_events2.data_source = 'linked_courses'
    hobby_with_events2.origin_id = 'foo:2'
    hobby_with_events2.save()
    event = hobby_with_events2.events.all()[0]
    event.data_source = 'linked_courses'
    event.origin_id = 'foo:3'
    event.save()
    event = hobby_with_events2.events.all()[1]
    event.data_source = 'linked_courses'
    event.origin_id = 'foo:4'
    event.save()
    return hobby_with_events2
