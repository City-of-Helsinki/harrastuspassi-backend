import datetime
import pytest
from freezegun import freeze_time
from django.core.files.base import ContentFile
from harrastuspassi.management.commands.import_lipas import Command as LipasImportCommand
from harrastuspassi.models import Hobby, HobbyEvent

pytest_plugins = ['harrastuspassi.tests.fixtures_lipas']


@pytest.mark.django_db
def test_deletions_none_deleted(imported_hobby, imported_hobby2):
    command = LipasImportCommand()
    hobby_qs = Hobby.objects.filter(data_source='lipas')
    event_qs = HobbyEvent.objects.filter(data_source='lipas')
    assert hobby_qs.count() == 2
    assert event_qs.count() == 4
    found_hobby_origin_ids = ['foo:1', 'foo:2']
    found_hobbyevent_origin_ids = ['foo:1', 'foo:2', 'foo:3', 'foo:4']
    command.handle_deletions(found_hobby_origin_ids, found_hobbyevent_origin_ids)
    assert hobby_qs.count() == 2
    assert event_qs.count() == 4


@pytest.mark.django_db
def test_deletions_hobby_deleted(imported_hobby, imported_hobby2):
    command = LipasImportCommand()
    hobby_qs = Hobby.objects.filter(data_source='lipas')
    event_qs = HobbyEvent.objects.filter(data_source='lipas')
    assert hobby_qs.count() == 2
    assert event_qs.count() == 4
    found_hobby_origin_ids = ['foo:1']
    found_hobbyevent_origin_ids = ['foo:1', 'foo:2', 'foo:3', 'foo:4']
    command.handle_deletions(found_hobby_origin_ids, found_hobbyevent_origin_ids)
    assert hobby_qs.count() == 1
    assert event_qs.count() == 2


@pytest.mark.django_db
def test_deletions_hobbyevent_deleted(imported_hobby, imported_hobby2):
    command = LipasImportCommand()
    hobby_qs = Hobby.objects.filter(data_source='lipas')
    event_qs = HobbyEvent.objects.filter(data_source='lipas')
    assert hobby_qs.count() == 2
    assert event_qs.count() == 4
    found_hobby_origin_ids = ['foo:1', 'foo:2']
    found_hobbyevent_origin_ids = ['foo:1', 'foo:2', 'foo:3']
    command.handle_deletions(found_hobby_origin_ids, found_hobbyevent_origin_ids)
    assert hobby_qs.count() == 2
    assert event_qs.count() == 3


@pytest.mark.django_db
def test_deletions_hobby_and_events_deleted(imported_hobby, imported_hobby2):
    command = LipasImportCommand()
    hobby_qs = Hobby.objects.filter(data_source='lipas')
    event_qs = HobbyEvent.objects.filter(data_source='lipas')
    assert hobby_qs.count() == 2
    assert event_qs.count() == 4
    found_hobby_origin_ids = ['foo:1']
    found_hobbyevent_origin_ids = ['foo:1', 'foo:2']
    command.handle_deletions(found_hobby_origin_ids, found_hobbyevent_origin_ids)
    assert hobby_qs.count() == 1
    assert event_qs.count() == 2

