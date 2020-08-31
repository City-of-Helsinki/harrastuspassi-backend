# -*- coding: utf-8 -*-
from datetime import date
from django.core.management.base import BaseCommand
from django.db import models
from harrastuspassi.models import Hobby, HobbyEvent


class Command(BaseCommand):
    def handle(self, *args, **options):
        start_date_in_future_count = Hobby.objects.update(
            next_event_id=models.Subquery(
                HobbyEvent.objects.filter(
                    hobby=models.OuterRef('pk'),
                    start_date__gte=date.today()
                )
                .values_list('id')
                .order_by('start_date')[:1]
            )
        )
        end_date_in_future_count = Hobby.objects.filter(next_event_id__isnull=True).update(
            next_event_id=models.Subquery(
                HobbyEvent.objects.filter(
                    hobby=models.OuterRef('pk'),
                    end_date__gte=date.today()
                )
                .values_list('id')
                .order_by('start_date')[:1]
            )
        )
