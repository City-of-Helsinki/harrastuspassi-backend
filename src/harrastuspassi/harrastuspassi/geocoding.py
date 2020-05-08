# -*- coding: utf-8 -*-
import logging

import requests
from django.contrib.gis.geos import Point
from rest_framework.exceptions import APIException

from harrastuspassi import settings

LOG = logging.getLogger(__name__)


def get_coordinates_from_address(address):
    payload = {
        'key': settings.GOOGLE_GEOCODING_API_KEY,
        'address': address
    }
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    try:
        response = requests.get(url, params=payload, timeout=settings.DEFAULT_REQUESTS_TIMEOUT)
        location_data = response.json()
    except requests.exceptions.RequestException:
        LOG.error(
            "Invalid response from GeoCoding API",
            extra={
                "data": {
                    "status_code": response.status_code,
                    "location_data": repr(response.content),
                }
            },
        )
    if not location_data['status'] == 'OK':
        raise APIException('Could not geocode given address')
    lat = location_data['results'][0]['geometry']['location']['lat']
    lon = location_data['results'][0]['geometry']['location']['lng']
    return Point(lon, lat)
