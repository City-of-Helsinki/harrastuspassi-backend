
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from harrastuspassi.tasks import update_promotion_permissions
from harrastuspassi.models import Promotion


class Command(BaseCommand):
    def handle(self, *args, **options):
        total_count = Promotion.objects.all().count()
        current_count = 0
        for promotion_id in Promotion.objects.all().values_list('id', flat=True):
            current_count += 1
            self.stdout.write(f'Updating {current_count} out of {total_count}')
            update_promotion_permissions(promotion_id)
