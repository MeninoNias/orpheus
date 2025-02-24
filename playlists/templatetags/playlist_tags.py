from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def format_duration(seconds):
    """
    Converte segundos em formato mm:ss
    """
    if not seconds:
        return "00:00"
    
    try:
        seconds = int(seconds)
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}:{remaining_seconds:02d}"
    except (ValueError, TypeError):
        return "00:00"