from django.utils import translation
from django.utils.translation import get_language
from .translations import SWAHILI_TRANSLATIONS

class SwahiliTranslationMiddleware:
    """
    Middleware to handle custom Swahili translations when Django's translation files are not available
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Store the original translation function
        original_gettext = translation.gettext
        original_ngettext = translation.ngettext
        
        def custom_gettext(message):
            """Custom gettext function that checks for Swahili translations"""
            language = get_language()
            if language == 'sw' and message in SWAHILI_TRANSLATIONS:
                return SWAHILI_TRANSLATIONS[message]
            return original_gettext(message)
        
        def custom_ngettext(singular, plural, number):
            """Custom ngettext function"""
            language = get_language()
            if language == 'sw' and singular in SWAHILI_TRANSLATIONS:
                return SWAHILI_TRANSLATIONS[singular]
            return original_ngettext(singular, plural, number)
        
        # Replace the translation functions
        translation.gettext = custom_gettext
        translation.ngettext = custom_ngettext
        
        response = self.get_response(request)
        
        # Restore original functions
        translation.gettext = original_gettext
        translation.ngettext = original_ngettext
        
        return response
