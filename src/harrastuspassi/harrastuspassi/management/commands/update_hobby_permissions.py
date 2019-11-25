
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from harrastuspassi.tasks import update_hobby_permissions
from harrastuspassi.models import Hobby


class Command(BaseCommand):
    def handle(self, *args, **options):
        total_count = Hobby.objects.all().count()
        current_count = 0
        for hobby_id in Hobby.objects.all().values_list('id', flat=True):
            current_count += 1
            self.stdout.write(f'Updating {current_count} out of {total_count}')
            update_hobby_permissions(hobby_id)
