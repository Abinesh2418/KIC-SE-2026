from django import template

register = template.Library()


@register.filter
def getfield(form, field_name):
    """Access a form field by dynamic name in templates."""
    return form[field_name]


@register.filter
def get_item(dictionary, key):
    """Access a dict value by key in templates."""
    return dictionary.get(key, 0)


@register.filter
def ms_to_time(value):
    """Convert milliseconds to 'Xm Ys' format."""
    try:
        ms = int(value)
        total_seconds = ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        if minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"
    except (ValueError, TypeError):
        return "—"
