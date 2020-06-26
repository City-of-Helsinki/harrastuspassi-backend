from modeltranslation.translator import translator, TranslationOptions
from .models import HobbyCategory


class HobbyCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(HobbyCategory, HobbyCategoryTranslationOptions)