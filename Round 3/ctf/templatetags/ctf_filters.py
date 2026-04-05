from django import template

register = template.Library()


@register.filter
def lookup(d, key):
    """Dictionary lookup by key in templates: dict|lookup:key"""
    if isinstance(d, dict):
        return d.get(key)
    return None


@register.filter
def percentage(value, total):
    """Calculate percentage: value|percentage:total"""
    try:
        return int(float(value) / float(total) * 100)
    except (ValueError, ZeroDivisionError):
        return 0
