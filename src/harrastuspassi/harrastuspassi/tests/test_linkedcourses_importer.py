import pdb
import datetime
import pytest
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
    event['offers'] = {'is_free': 'true'}
    assert command.get_price_type(event) == Hobby.TYPE_FREE 
    event['offers'] = {'is_free': 'false'}
    assert command.get_price_type(event) == Hobby.TYPE_PAID
    event['offers'] = {'is_free': '', 'price':'0.0'}
    assert command.get_price_type(event) == Hobby.TYPE_FREE
    event['offers'] = {'is_free': '', 'price':'1.0'}
    assert command.get_price_type(event) == Hobby.TYPE_PAID


@pytest.mark.django_db
def test_price_import(basic_event):
    command = LinkedCoursesImportCommand()
    event = basic_event
    event['offers'] = []
    assert command.get_price(event) == 0
    event['offers'] = {'price': '10.0'}
    assert command.get_price(event) == 10 
    event['offers'] = {'price': ''}
    assert command.get_price(event) == 0
    event['offers'] = {'price': None}
    assert command.get_price(event) == 0
