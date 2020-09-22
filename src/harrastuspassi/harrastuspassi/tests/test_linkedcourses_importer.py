import datetime
import pytest
from decimal import Decimal
from freezegun import freeze_time
from django.core.files.base import ContentFile
from harrastuspassi.management.commands.import_linkedcourses import Command as LinkedCoursesImportCommand
from harrastuspassi.models import Hobby, HobbyEvent
from harrastuspassi.tests.conftest import FROZEN_DATETIME

pytest_plugins = ['harrastuspassi.tests.fixtures_linkedcourses']


@freeze_time(FROZEN_DATETIME)
@pytest.mark.django_db
def test_event_image_update(mocker, hobby, event_with_images_only, frozen_datetime):
    command = LinkedCoursesImportCommand()

    command.fetch_image = mocker.Mock(return_value=(ContentFile('foo'), 'foo.jpg'), name='fetch_image')
    # New image
    event = event_with_images_only
    event['images'][0]['last_modified_time'] = (frozen_datetime - datetime.timedelta(days=30)).isoformat() + 'Z'
    command.handle_hobby_cover_image(event, hobby)
    command.fetch_image.assert_called()
    command.fetch_image.reset_mock()
    # Same image, same last_modified_time
    command.handle_hobby_cover_image(event, hobby)
    command.fetch_image.assert_not_called()
    command.fetch_image.reset_mock()
    # Same image, newer last_modified_time
    event['images'][0]['last_modified_time'] = (frozen_datetime - datetime.timedelta(days=5)).isoformat() + 'Z'
    command.handle_hobby_cover_image(event, hobby)
    command.fetch_image.assert_called()


@pytest.mark.django_db
def test_deletions_none_deleted(imported_hobby, imported_hobby2):
    command = LinkedCoursesImportCommand()
    command.source = 'linked_courses'
    hobby_qs = Hobby.objects.filter(data_source='linked_courses')
    event_qs = HobbyEvent.objects.filter(data_source='linked_courses')
    assert hobby_qs.count() == 2
    assert event_qs.count() == 4
    found_hobby_origin_ids = ['foo:1', 'foo:2']
    found_hobbyevent_origin_ids = ['foo:1', 'foo:2', 'foo:3', 'foo:4']
    command.handle_deletions(found_hobby_origin_ids, found_hobbyevent_origin_ids)
    assert hobby_qs.count() == 2
    assert event_qs.count() == 4


@pytest.mark.django_db
def test_deletions_hobby_deleted(imported_hobby, imported_hobby2):
    command = LinkedCoursesImportCommand()
    command.source = 'linked_courses'
    hobby_qs = Hobby.objects.filter(data_source='linked_courses')
    event_qs = HobbyEvent.objects.filter(data_source='linked_courses')
    assert hobby_qs.count() == 2
    assert event_qs.count() == 4
    found_hobby_origin_ids = ['foo:1']
    found_hobbyevent_origin_ids = ['foo:1', 'foo:2', 'foo:3', 'foo:4']
    command.handle_deletions(found_hobby_origin_ids, found_hobbyevent_origin_ids)
    assert hobby_qs.count() == 1
    assert event_qs.count() == 2


@pytest.mark.django_db
def test_deletions_hobbyevent_deleted(imported_hobby, imported_hobby2):
    command = LinkedCoursesImportCommand()
    command.source = 'linked_courses'
    hobby_qs = Hobby.objects.filter(data_source='linked_courses')
    event_qs = HobbyEvent.objects.filter(data_source='linked_courses')
    assert hobby_qs.count() == 2
    assert event_qs.count() == 4
    found_hobby_origin_ids = ['foo:1', 'foo:2']
    found_hobbyevent_origin_ids = ['foo:1', 'foo:2', 'foo:3']
    command.handle_deletions(found_hobby_origin_ids, found_hobbyevent_origin_ids)
    assert hobby_qs.count() == 2
    assert event_qs.count() == 3


@pytest.mark.django_db
def test_deletions_hobby_and_events_deleted(imported_hobby, imported_hobby2):
    command = LinkedCoursesImportCommand()
    command.source = 'linked_courses'
    hobby_qs = Hobby.objects.filter(data_source='linked_courses')
    event_qs = HobbyEvent.objects.filter(data_source='linked_courses')
    assert hobby_qs.count() == 2
    assert event_qs.count() == 4
    found_hobby_origin_ids = ['foo:1']
    found_hobbyevent_origin_ids = ['foo:1', 'foo:2']
    command.handle_deletions(found_hobby_origin_ids, found_hobbyevent_origin_ids)
    assert hobby_qs.count() == 1
    assert event_qs.count() == 2


@pytest.mark.django_db
def test_price_type_import(basic_event):
    command = LinkedCoursesImportCommand()
    event = basic_event
    event['offers'] = []
    assert command.get_price_type(event) == Hobby.TYPE_FREE
    event['offers'] = [{'is_free': 'true'}]
    assert command.get_price_type(event) == Hobby.TYPE_FREE
    event['offers'] = [{'is_free': 'false', 'price': 'null', 'info_url': 'null', 'description': 'null'}]
    assert command.get_price_type(event) == Hobby.TYPE_FREE
    event['offers'] = [{'is_free': 'false', 'price': {'fi': 'VaPaA pääsy.'}, 'info_url': 'null'}]
    assert command.get_price_type(event) == Hobby.TYPE_FREE
    event['offers'] = [{'is_free': 'false', 'price': {'fi': '10/20/30$'}}]
    assert command.get_price_type(event) == Hobby.TYPE_PAID
    event['offers'] = [{'is_free': 'false', 'price': 'null', 'info_url': 'https://buythetickets.here'}]
    assert command.get_price_type(event) == Hobby.TYPE_PAID
    event['offers'] = [{'is_free': 'false', 'price': 'null', 'info_url': 'null',
                        'description': {'fi': 'Tickets from Jenni 044832932'}}]
    assert command.get_price_type(event) == Hobby.TYPE_PAID


@pytest.mark.django_db
def test_price_import(basic_event):
    command = LinkedCoursesImportCommand()
    event = basic_event
    event['offers'] = []
    assert command.get_price(event) == Decimal(0)
    event['offers'] = [{'price': {'fi': '10.0'}}]
    assert command.get_price(event) == Decimal(10)
    event['offers'] = [{'price': {'fi': 'funny circus 10/20/30$'}}]
    assert command.get_price(event) == Decimal(10)
    event['offers'] = [{'price': {'fi': 'Vapaa pÄÄsy!'}}]
    assert command.get_price(event) == Decimal(0)


@pytest.mark.django_db
def test_description_import(basic_event):
    command = LinkedCoursesImportCommand()
    event = basic_event
    event['short_description'] = {'fi': 'Short description'}
    event['description'] = {'fi': '<p>Poesian ja Runokuun \n\r \xa0 \x1fyhteisillassa.</p><p>Ovet klo 19:00.<br>htumaan.</p><p>Esiintyjät: </p>'}  # noqa: E501
    event['offers'] = [{'info_url': {'fi': 'https://ticketshere.info'}, 'description': {'fi': 'Offers description.'}, 'price': {'fi': "65"}}]  # noqa: E501
    assert command.get_description(event) == 'Short description Kenelle: 12-17v. Offers description. https://ticketshere.info'  # noqa: E501
    event['short_description'] = {'fi': ''}
    event['audience_min_age'] = None
    event['audience_max_age'] = None
    assert command.get_description(event) == 'Offers description. https://ticketshere.info Poesian ja Runokuun yhteisillassa.Ovet klo 19:00.htumaan.Esiintyjät:'  # noqa: E501
    event['audience_max_age'] = 17
    event['short_description'] = 'null'
    assert command.get_description(event) == 'Offers description. https://ticketshere.info Kenelle: -17v. Poesian ja Runokuun yhteisillassa.Ovet klo 19:00.htumaan.Esiintyjät:'  # noqa: E501
    event['offers'] = [{'info_url': 'null', 'description': {'fi': 'Offers description.'}}]
    event['audience_min_age'] = 12
    event['audience_max_age'] = None
    assert command.get_description(event) == 'Offers description. Kenelle: 12v.- Poesian ja Runokuun yhteisillassa.Ovet klo 19:00.htumaan.Esiintyjät:'  # noqa: E501
    event['offers'] = [{'info_url': 'null', 'description': 'null'}]
    event['audience_min_age'] = None
    assert command.get_description(event) == 'Poesian ja Runokuun yhteisillassa.Ovet klo 19:00.htumaan.Esiintyjät:'
    event['offers'] = [{'info_url': 'None', 'description': 'None'}]
    assert command.get_description(event) == 'Poesian ja Runokuun yhteisillassa.Ovet klo 19:00.htumaan.Esiintyjät:'
    event['offers'] = [{'info_url': '', 'description': ''}]
    assert command.get_description(event) == 'Poesian ja Runokuun yhteisillassa.Ovet klo 19:00.htumaan.Esiintyjät:'
    event['offers'] = []
    assert command.get_description(event) == 'Poesian ja Runokuun yhteisillassa.Ovet klo 19:00.htumaan.Esiintyjät:'
    event['short_description'] = {'en': 'Short description'}
    assert command.get_description(event) == 'Poesian ja Runokuun yhteisillassa.Ovet klo 19:00.htumaan.Esiintyjät:'


@pytest.mark.django_db
def test_event_with_no_keywords(basic_event):
    command = LinkedCoursesImportCommand()
    event = basic_event
    event['keywords'] = []
    assert command.handle_event(event) == []


@pytest.mark.django_db
def test_orphaned_event(basic_event):
    command = LinkedCoursesImportCommand()
    command.source = 'linked_courses'
    event = basic_event
    event['super_event'] = {'@id': 'https://hobby-not-created-yet'}
    hobbyevent = command.handle_hobby_event(event)
    assert str(hobbyevent) == 'Orphan HobbyEvent with no Hobby'
    hobbyevents = [hobbyevent]
    command.handle_orphaned_hobby_events(hobbyevents)
    assert HobbyEvent.objects.count() == 0
    Hobby(name='test',
          data_source=command.source,
          origin_id=hobbyevent._hobby_origin_id).save()
    command.handle_orphaned_hobby_events(hobbyevents)
    assert HobbyEvent.objects.count() == 1
