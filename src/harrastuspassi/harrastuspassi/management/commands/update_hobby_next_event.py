# -*- coding: utf-8 -*-
from datetime import date
from django.core.management.base import BaseCommand
from django.db import models
from harrastuspassi.models import Hobby, HobbyEvent


class Command(BaseCommand):
    """ Update next event for each Hobby """
    def handle(self, *args, **options):
        # Prefer upcoming events over ongoing events
        updated_count = Hobby.objects.update(
            next_event_id=models.Subquery(
                HobbyEvent.objects.filter(
                    hobby=models.OuterRef('pk'),
                    start_date__gte=date.today()
                )
                .values_list('id')
                .order_by('start_date')[:1]
            )
        )
        self.stdout.write(f'Updated {updated_count} hobbies')
        # If there are Hobbies with only ongoing events and no upcoming events
        # then fall back to the ongoing event
        fallback_updated_count = Hobby.objects.filter(next_event_id__isnull=True).update(
            next_event_id=models.Subquery(
                HobbyEvent.objects.filter(
                    hobby=models.OuterRef('pk'),
                    end_date__gte=date.today()
                )
                .values_list('id')
                .order_by('start_date')[:1]
            )
        )
        self.stdout.write(f'Updated {fallback_updated_count} hobbies with fallback query')
        hobbies_without_next_event_count = Hobby.objects.filter(next_event_id__isnull=True).count()
        start_date_in_future_count = updated_count - fallback_updated_count
        end_date_in_future_count = fallback_updated_count - hobbies_without_next_event_count
        self.stdout.write(f'{start_date_in_future_count} hobbies with upcoming next event')
        self.stdout.write(f'{end_date_in_future_count} hobbies with ongoing next event')
        self.stdout.write(f'{hobbies_without_next_event_count} hobbies without next event')