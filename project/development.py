
# -*- coding: utf-8 -*-
#
# Copyright Haltu Oy, info@haltu.fi
# All rights reserved.
#

#- This file documents what are the settings needed in development
#-
#- Infrastructure specific settings come from local_settings.py
#- which is importing this file.

from project.settings import *

DEBUG = True
TEMPLATE_DEBUG = True

# Compress
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_HTML = True

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2

