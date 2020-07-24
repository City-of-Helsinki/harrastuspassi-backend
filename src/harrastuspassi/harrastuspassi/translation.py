from modeltranslation.translator import translator, TranslationOptions
from .models import HobbyCategory, HobbyAudience


class HobbyCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)


class HobbyAudienceTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(HobbyCategory, HobbyCategoryTranslationOptions)
translator.register(HobbyAudience, HobbyAudienceTranslationOptions)
