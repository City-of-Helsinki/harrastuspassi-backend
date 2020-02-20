
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from harrastuspassi.tasks import update_location_permissions
from harrastuspassi.models import Location


class Command(BaseCommand):
    def handle(self, *args, **options):
        total_count = Location.objects.all().count()
        current_count = 0
        for location_id in Location.objects.all().values_list('id', flat=True):
            current_count += 1
            self.stdout.write(f'Updating {current_count} out of {total_count}')
            update_location_permissions(location_id)
