
# -*- coding: utf-8 -*-
# - This file documents what are the settings needed in development
# -
# - Infrastructure specific settings come from local_settings.py
# - which is importing this file.

from project.settings import *  # noqa

DEBUG = True
TEMPLATE_DEBUG = True

# CORS headers for local development
INSTALLED_APPS += ('corsheaders',)
MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware'] + MIDDLEWARE
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = ['http://localhost:3000']
CORS_ALLOW_CREDENTIALS = True

# Compress
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_HTML = True
