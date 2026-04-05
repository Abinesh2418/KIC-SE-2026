from .models import SiteSettings


def global_context(request):
    """Add global variables to all templates."""
    settings = SiteSettings.get()
    ctx = {
        'event_active': settings.event_active,
        'leaderboard_public': settings.leaderboard_public,
        'challenges_revealed': settings.challenges_revealed,
    }
    if request.user.is_authenticated:
        ctx['display_points'] = request.user.total_points
    return ctx
