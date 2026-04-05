"""
Middleware that dynamically trusts the Origin / Referer of every incoming
request for CSRF purposes.

Django 4.0+ enforces CSRF_TRUSTED_ORIGINS for every POST when DEBUG=False.
On a LAN served over plain HTTP on IP addresses (e.g. http://10.1.75.185:7739),
there is no practical way to enumerate every origin in advance.

This middleware runs *before* CsrfViewMiddleware and adds the current
request's origin to CSRF_TRUSTED_ORIGINS on-the-fly.  The CSRF *token*
check (cookie ↔ form-field / X-CSRFToken header) remains fully active.
"""
from urllib.parse import urlparse
from django.conf import settings


class DynamicCSRFTrustedOriginMiddleware:
    """Insert BEFORE django.middleware.csrf.CsrfViewMiddleware in MIDDLEWARE."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origins_to_add = set()

        origin = request.META.get('HTTP_ORIGIN')
        if origin:
            origins_to_add.add(origin.rstrip('/'))

        referer = request.META.get('HTTP_REFERER')
        if referer:
            parsed = urlparse(referer)
            if parsed.scheme and parsed.netloc:
                origins_to_add.add(f'{parsed.scheme}://{parsed.netloc}')

        for o in origins_to_add:
            if o not in settings.CSRF_TRUSTED_ORIGINS:
                settings.CSRF_TRUSTED_ORIGINS.append(o)

        return self.get_response(request)
