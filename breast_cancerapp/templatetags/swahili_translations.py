from django import template
from ..translations import get_translation

register = template.Library()

@register.filter
def sw_trans(text):
    """Template filter for Swahili translation"""
    try:
        from django.utils.translation import get_language
        language = get_language()
        return get_translation(text, language)
    except:
        return text

@register.simple_tag
def sw_trans_tag(text):
    """Template tag for Swahili translation"""
    try:
        from django.utils.translation import get_language
        language = get_language()
        return get_translation(text, language)
    except:
        return text

@register.simple_tag
def trans_text(text, language='sw'):
    """Translation tag with explicit language"""
    return get_translation(text, language)
