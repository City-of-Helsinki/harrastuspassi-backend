
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
      [origin_id] = subclass.identifier or ['']
      if not origin_id:
        data_source = ''
      else:
        data_source = 'yso'
      labels = subclass.label

      name_fi, name_sv, name_en = '', '', ''
      for label in labels:
        label_lang = getattr(label, 'lang', 'fi')
        if label_lang == 'fi':
          name_fi = label
        elif label_lang == 'sv':
          name_sv = label
        elif label_lang == 'en':
          name_en = label
      hobby_category, created = HobbyCategory.objects.update_or_create(
        name=name_fi,
        parent=parent_hobby_category,
        defaults={
          'name_fi': name_fi,
          'name_sv': name_sv,
          'name_en': name_en,
          'data_source': data_source,
          'origin_id': origin_id
        }
      )
      indent = '--' * self.depth
      self.stdout.write(f'{indent}fi_{name_fi}, sv_{name_sv}, en_{name_en}')
      self.depth += 1
      self.add_subclasses_as_categories(subclass, hobby_category)
      self.depth -= 1
