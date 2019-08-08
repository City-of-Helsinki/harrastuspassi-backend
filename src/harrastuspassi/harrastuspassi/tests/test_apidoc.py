
# -*- coding: utf-8 -*-

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_api_documentation(client):
    """ ReDoc API documentation URL should return success to GET request """
    url = reverse('redoc')
    response = client.get(url)
    assert response.status_code == 200
    assert 'text/html' in response['content-type'], "Response should be HTML"


@pytest.mark.django_db
def test_openapi(client):
    """ OpenAPI URL should return success to GET request """
    url = reverse('openapi-schema')
    headers = {'Accept': 'application/vnd.oai.openapi'}
    response = client.get(url, headers=headers)
    assert response.status_code == 200
    assert 'application/vnd.oai.openapi' in response['content-type'], "Response should be OpenAPI spec"
