"""
Custom middleware for security, quota enforcement, and performance monitoring.
"""
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.conf import settings


class QuotaMiddleware:
    """Enforce query rate limits on research endpoints."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only check POST to research endpoints
        if request.method == 'POST' and '/research/' in request.path:
            if request.user.is_authenticated:
                profile = request.user.profile

                if not profile.can_make_query():
                    msg = f"Hourly quota exceeded ({profile.quota_limit}/hour). Resets at {profile.quota_reset_at.strftime('%H:%M')}."

                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            "status": "error",
                            "message": msg,
                            "quota": profile.get_quota_status()
                        }, status=429)

                    messages.error(request, msg)
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

                # Increment on successful submission (handled in view after validation)
                request._quota_checked = True

        response = self.get_response(request)
        return response


class ContentSecurityPolicyMiddleware:
    """
    Add Content-Security-Policy headers to all responses.
    Addresses NF-SEC-005 requirement.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Build CSP header from settings
        csp_directives = []

        if hasattr(settings, 'CSP_DEFAULT_SRC'):
            csp_directives.append(f"default-src {' '.join(settings.CSP_DEFAULT_SRC)}")
        else:
            csp_directives.append("default-src 'self'")

        if hasattr(settings, 'CSP_SCRIPT_SRC'):
            csp_directives.append(f"script-src {' '.join(settings.CSP_SCRIPT_SRC)}")
        else:
            csp_directives.append("script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com")

        if hasattr(settings, 'CSP_STYLE_SRC'):
            csp_directives.append(f"style-src {' '.join(settings.CSP_STYLE_SRC)}")
        else:
            csp_directives.append("style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com")

        if hasattr(settings, 'CSP_IMG_SRC'):
            csp_directives.append(f"img-src {' '.join(settings.CSP_IMG_SRC)}")
        else:
            csp_directives.append("img-src 'self' data: https:")

        if hasattr(settings, 'CSP_FONT_SRC'):
            csp_directives.append(f"font-src {' '.join(settings.CSP_FONT_SRC)}")
        else:
            csp_directives.append("font-src 'self'")

        if hasattr(settings, 'CSP_CONNECT_SRC'):
            csp_directives.append(f"connect-src {' '.join(settings.CSP_CONNECT_SRC)}")
        else:
            csp_directives.append("connect-src 'self'")

        if hasattr(settings, 'CSP_FRAME_ANCESTORS'):
            csp_directives.append(f"frame-ancestors {' '.join(settings.CSP_FRAME_ANCESTORS)}")
        else:
            csp_directives.append("frame-ancestors 'none'")

        response['Content-Security-Policy'] = '; '.join(csp_directives)

        # Additional security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'

        return response


class RequestTimingMiddleware:
    """Add request timing header for performance monitoring."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        import time
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time
        response['X-Request-Duration'] = f"{duration:.3f}s"
        return response