from django.shortcuts import redirect
from django.utils.translation import activate
from django.urls import translate_url


def set_language(request):
    """
    Set language for the session and redirect to the same page in the new language.
    """
    lang_code = request.GET.get('lang', 'en')
    next_url = request.GET.get('next', request.META.get('HTTP_REFERER', '/'))
    
    # Validate language code
    from django.conf import settings
    available_languages = [lang[0] for lang in settings.LANGUAGES]
    
    if lang_code in available_languages:
        activate(lang_code)
        request.session['django_language'] = lang_code
        
        # Translate the next URL if possible
        try:
            next_url = translate_url(next_url, lang_code)
        except:
            pass
    
    return redirect(next_url)
