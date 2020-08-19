import datetime
import pytest


@pytest.fixture
def basic_event():
    return {
        "id": "harrastushaku:13248",
        "location": {
            "@id": "https://api.hel.fi/linkedcourses/v1/place/tprek:8020/"
        },
        "keywords": [{
            "@id": "https://api.hel.fi/linkedcourses/v1/keyword/yso:p23125/"
        }],
        "super_event": None,
        "event_status": "EventRescheduled",
        "external_links": [],
        "offers": [],
        "data_source": "harrastushaku",
        "publisher": "ahjo:u48040030",
        "sub_events": [],
        "images": [{
            "id": 2531,
            "license": "cc_by",
            "created_time": "2020-06-10T11:15:57.772163Z",
            "last_modified_time": "2020-06-10T11:15:57.772182Z",
            "name": "",
            "url": "https://www.harrastushaku.fi/images/activityimages/6135_0232.JPG",
            "cropping": "",
            "photographer_name": None,
            "alt_text": None,
            "data_source": "harrastushaku",
            "publisher": "ahjo:u48040030",
            "@id": "https://api.hel.fi/linkedcourses/v1/image/2531/",
            "@context": "http://schema.org",
            "@type": "ImageObject"
        }],
        "videos": [],
        "in_language": [],
        "audience": [{
            "@id": "https://api.hel.fi/linkedcourses/v1/keyword/yso:p11617/"
        }, {
            "@id": "https://api.hel.fi/linkedcourses/v1/keyword/yso:p16485/"
        }],
        "created_time": "2020-06-12T06:15:44.181210Z",
        "last_modified_time": "2020-07-30T12:19:11.898081Z",
        "date_published": "2020-07-30T11:17:00Z",
        "start_time": "2020-08-22",
        "end_time": "2020-08-22",
        "custom_data": None,
        "audience_min_age": 12,
        "audience_max_age": 17,
        "super_event_type": None,
        "deleted": False,
        "replaced_by": None,
        "extension_course": {
            "enrolment_start_time": None,
            "enrolment_end_time": None,
            "maximum_attendee_capacity": 35,
            "minimum_attendee_capacity": None,
            "remaining_attendee_capacity": 1
        },
        "location_extra_info": None,
        "description": {
            "fi": "<p> <span style='background - color: initial;''>Työnjaossa pääset siivoamaan\
            karsinoita ja tekemään muita navettatöitä, hoitamaan ja puuhailemaan erilaisten eläinten\
            kanssa sekä ruokkimaan eläimiä. Voit esimerkiksi päästä taluttamaan lehmää, hypyttämään\
            vuohta agility radalla, harjaamaan kania tai jopa ratsastamaan. Työnjako alkaa klo 10.30\
            ja loppuu klo 15. Ota mukaan säänmukaiset ja navettaan sopivat vaatteet sekä kumisaappaat,\
            osa päivästä ollaan ulkona. Toimintapäiviin sisältyy yhteinen ruokatauko, jolloin syödään\
            omia eväitä. </span> </p>"
        },
        "provider_contact_info": None,
        "provider": None,
        "name": {
            "fi": "Lauantai työnjako 22.8."
        },
        "info_url": None,
        "short_description": None,
        "@id": "https://api.hel.fi/linkedcourses/v1/event/harrastushaku:13248/",
        "@context": "http://schema.org",
        "@type": "Event/LinkedEvent"
}


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
