
# -*- coding: utf-8 -*-

from django.apps import AppConfig


class DefaultConfig(AppConfig):
    name = 'harrastuspassi'
    verbose_name = 'harrastuspassi'

    def ready(self):
        from harrastuspassi import receivers  # noqa; pylint: disable=unused-import
