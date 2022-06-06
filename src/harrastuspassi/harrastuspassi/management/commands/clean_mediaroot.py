import os

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import models


class Command(BaseCommand):
    help = 'Clean media by deleting those files which are no more referenced by any FileField'

    def add_arguments(self, parser):
        parser.add_argument(
            '--noinput',
            action = 'store_true',
            default = False,
            help = 'Clean media by deleting those files which are no more referenced by any FileField without asking for confirmation'
        )

    def handle(self, *args, **options):
        exclude_paths = ('cache', )  # Exclude cache folder by default since generally it's used by third-party apps
        exclude_roots = [ os.path.normpath(settings.MEDIA_ROOT + '/' + path) for path in exclude_paths ]

        # Build a list of all media files used by our models
        models_files = []

        for model in apps.get_models():

            model_objects = list(model.objects.all())
            model_file_fields = []

            for field_name in [f.name for f in model._meta.get_fields()]:
                field = model._meta.get_field(field_name)

                if isinstance(field, models.FileField):
                    model_file_fields.append(str(field_name))

            if not len(model_file_fields):
                continue

            for obj in model_objects:
                for field in model_file_fields:
                    file = getattr(obj, field, '')
                    if file:
                        models_files.append(file.path)

        unref_files = []

        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            exclude_root = False
            for excluded_root in exclude_roots:
                if root.find(excluded_root) == 0:
                    exclude_root = True
                    break

            if exclude_root:
                continue

            for file in files:
                file_path = os.path.join(root, file)
                if not file_path in models_files:
                    unref_files.append(file_path)

        for file in unref_files:
            print('found unreferenced file: %s' % (file ))
        num_unref_files = len(unref_files)
        print('found %s unreferenced file%s' % (num_unref_files, 's' if num_unref_files else '', ))
        if num_unref_files:
            remove_unref_files = True if options['noinput'] else (input('remove all unreferenced files? (y/N) ').lower().find('y') == 0)
            if remove_unref_files:
                for file in unref_files:
                    try:
                        os.remove(file)
                        print('removed unreferenced file: %s' % (file ))
                    except:
                        continue
        return
