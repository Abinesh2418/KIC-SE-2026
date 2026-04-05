from django import template

register = template.Library()


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
