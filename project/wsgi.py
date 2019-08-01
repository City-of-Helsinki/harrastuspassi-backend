# -*- coding: utf-8 -*-

import os
from django.core.wsgi import get_wsgi_application
from raven.contrib.django.raven_compat.middleware.wsgi import Sentry

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'local_settings')

application = Sentry(get_wsgi_application())

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2
