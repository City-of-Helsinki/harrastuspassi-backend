# -*- coding: utf-8 -*-

import pytest
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.mark.django_db
def test_get_jwt_token_session(user_api_client):
    """ GET request token obtain endpoint should return tokens for user """
    url = reverse('auth.token_obtain_pair')
    response = user_api_client.get(url)
    assert response.status_code == 200
    data = response.data
    assert 'refresh' in data
    assert 'access' in data


@pytest.mark.django_db
def test_get_jwt_token_unauthenticated(api_client):
    """ Unauthenticated user should not get tokens via GET """
    url = reverse('auth.token_obtain_pair')
    response = api_client.get(url)
    assert response.status_code == 401


@pytest.mark.django_db
def test_use_jwt_auth(api_client, user):
    """ Unauthenticated request with valid JWT authorization token should allow access """
    refresh_token = RefreshToken.for_user(user)
    access_token = refresh_token.access_token
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    data = {'name': 'Test Hobby'}
    response = api_client.post(reverse('hobby-list'), data=data)
    assert response.status_code == 201
