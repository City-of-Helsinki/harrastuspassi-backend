
# -*- coding: utf-8 -*-
from collections import namedtuple
from owlready2 import get_ontology
from harrastuspassi.models import HobbyCategory
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.conf import settings

# TODO: there must be a better way
app_label = settings.INSTALLED_APPS[0]

Root = namedtuple('Root', ['label', 'model_name'])

ROOT_CLASSES = {
    'categories': Root(label='Harrastusmuoto', model_name='hobbycategory'),
    'audiences': Root(label='Yleisö', model_name='hobbyaudience')}

class Command(BaseCommand):
  help = 'Import category and audience keywords from .owl file.'

  def add_arguments(self, parser):
    parser.add_argument('--path', action='store', dest='path_to_owl_file', default='./ontology.owl',
                         help='Provide a path to the .owl file.')
    parser.add_argument('--categories', action='store_const', dest='import_categories', default=False,
                          const='categories', help='Import the hobby categories (harrastusmuodot)')
    parser.add_argument('--audiences', action='store_const', dest='import_audiences', default=False,
                          const='audiences', help='Import the keywords that define the audience (koululaiset, lapset jne.).') 

  def handle(self, *args, **options):
    ontology = get_ontology(options['path_to_owl_file']).load()
    self.process_option(options['import_categories'], ontology)
    self.process_option(options['import_audiences'], ontology)
    if not any([options['import_categories'], options['import_audiences']]):
      self.stderr.write('Specify --categories and/or --audiences to import onotologies.')

  def process_option(self, option: str, ontology):
    if not option:
      return
    root_class = ontology.search_one(label=ROOT_CLASSES[option].label)
    self.depth = 0
    model = ContentType.objects.get(app_label=app_label,
                                         model=ROOT_CLASSES[option].model_name
                                    ).model_class()
    self.add_subclasses_as_categories(root_class, model)


  def add_subclasses_as_categories(self, parent_class, model, parent_hobby_category=None):
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
      hobby_category, created = model.objects.update_or_create(
        name_fi=name_fi,
        parent=parent_hobby_category,
        defaults={
          'name_sv': name_sv,
          'name_en': name_en,
          'data_source': data_source,
          'origin_id': origin_id
        }
      )
      indent = '--' * self.depth
      self.stdout.write(f'{indent}fi_{name_fi}, sv_{name_sv}, en_{name_en}')
      self.depth += 1
      self.add_subclasses_as_categories(subclass, model, hobby_category)
      self.depth -= 1
