from django.shortcuts import redirect
from django.urls import reverse, resolve, Resolver404


class ApprovalGateMiddleware:
    """
    Block unapproved users from accessing anything except
    auth pages, the home page, and static files.
    """
    ALLOWED_URL_NAMES = [
        'home', 'login', 'register', 'logout', 'pending_approval',
    ]
    ALLOWED_PREFIXES = ['/static/', '/media/', '/django-admin/']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_approved:
            # Allow certain paths
            path = request.path
            if any(path.startswith(p) for p in self.ALLOWED_PREFIXES):
                return self.get_response(request)

            try:
                resolved = resolve(path)
                if resolved.url_name in self.ALLOWED_URL_NAMES:
                    return self.get_response(request)
            except Resolver404:
                pass

            return redirect('pending_approval')

        return self.get_response(request)
