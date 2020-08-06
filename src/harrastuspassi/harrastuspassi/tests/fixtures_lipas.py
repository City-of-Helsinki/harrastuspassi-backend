import pytest


@pytest.fixture
def imported_hobby(hobby_with_events):
    hobby_with_events.data_source = 'lipas'
    hobby_with_events.origin_id = 'foo:1'
    hobby_with_events.save()
    event = hobby_with_events.events.all()[0]
    event.data_source = 'lipas'
    event.origin_id = 'foo:1'
    event.save()
    event = hobby_with_events.events.all()[1]
    event.data_source = 'lipas'
    event.origin_id = 'foo:2'
    event.save()
    return hobby_with_events


@pytest.fixture
def imported_hobby2(hobby_with_events2):
    hobby_with_events2.data_source = 'lipas'
    hobby_with_events2.origin_id = 'foo:2'
    hobby_with_events2.save()
    event = hobby_with_events2.events.all()[0]
    event.data_source = 'lipas'
    event.origin_id = 'foo:3'
    event.save()
    event = hobby_with_events2.events.all()[1]
    event.data_source = 'lipas'
    event.origin_id = 'foo:4'
    event.save()
    return hobby_with_events2
