
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from owlready2 import get_ontology
from harrastuspassi.models import HobbyCategory


ROOT_CLASS_LABEL = 'Harrastusmuoto'


class Command(BaseCommand):
  def add_arguments(self, parser):
    parser.add_argument('path_to_owl_file')

  def handle(self, *args, **options):
    ontology = get_ontology(options['path_to_owl_file']).load()
    root_class = ontology.search_one(label=ROOT_CLASS_LABEL)
    self.depth = 0
    self.add_subclasses_as_categories(root_class)

  def add_subclasses_as_categories(self, parent_class, parent_hobby_category=None):
    for subclass in parent_class.subclasses():
      [yso_id] = subclass.identifier or [None]
      [label] = subclass.label
      # NOTE: This comment is here for a purpose: yso data source is being worked in another branch
      # hobby_category = HobbyCategory.objects.create(name=label, parent=parent_hobby_category, data_source='yso', origin_id=yso_id)
      hobby_category = HobbyCategory.objects.create(name=label, parent=parent_hobby_category)
      indent = '--' * self.depth
      self.stdout.write(f'{indent}{label}')
      self.depth += 1
      self.add_subclasses_as_categories(subclass, hobby_category)
      self.depth -= 1
