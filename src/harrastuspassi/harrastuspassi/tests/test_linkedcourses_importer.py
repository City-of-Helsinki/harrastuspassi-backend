import datetime
import pytest
from freezegun import freeze_time
from django.core.files.base import ContentFile
from harrastuspassi.management.commands.import_linkedcourses import Command as LinkedCoursesImportCommand
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

