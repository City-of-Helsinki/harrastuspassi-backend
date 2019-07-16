
# -*- coding: utf-8 -*-
#
# Copyright Haltu Oy, info@haltu.fi
# All rights reserved.
#


from django.test import TransactionTestCase, mock
from django.contrib.sessions.middleware import SessionMiddleware
from django.test.client import RequestFactory

from django.contrib.auth.models import User
from app.tests import factories as f
from app import views


class TestView(TransactionTestCase):
  def setUp(self):
    self.factory = RequestFactory()
    self.middleware = SessionMiddleware()

  def test_redirect_to_login(self):
      r = self.client.get('/')
      self.assertEqual(r.status_code, 302)

  def test_index(self):
    user = User.objects.create(username='foo', email='foo@example.haltu.net')

    request = self.factory.get('/')
    request.user = user
    self.middleware.process_request(request)

    with self.assertTemplateUsed('app/views/index.html'):
      response = views.IndexView.as_view()(request)
      self.assertContains(response, text='Welcome to app app!', status_code=200, html=False)

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2

