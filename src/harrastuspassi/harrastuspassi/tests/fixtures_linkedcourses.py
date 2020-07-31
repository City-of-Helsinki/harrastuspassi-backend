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

