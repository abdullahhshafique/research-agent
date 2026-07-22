"""
General rate limiting for all endpoints.
Uses in-memory sliding window with IP-based tracking.
"""

import time
import logging
from typing import Dict, Tuple
from functools import wraps
from django.http import JsonResponse, HttpResponseTooManyRequests
from django.core.cache import cache

# NEW (fixed):
from django.http import JsonResponse, HttpResponse

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Sliding window rate limiter using Django cache.
    """

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def _get_key(self, identifier: str) -> str:
        """Generate cache key for rate limit tracking."""
        return f"rate_limit:{identifier}"

    def is_allowed(self, identifier: str) -> Tuple[bool, int, int]:
        """
        Check if request is allowed.

        Returns:
            (allowed, remaining, reset_after)
        """
        key = self._get_key(identifier)
        now = time.time()
        window_start = now - self.window_seconds

        # Get current window data
        data = cache.get(key, [])

        # Filter to current window
        data = [t for t in data if t > window_start]

        if len(data) >= self.max_requests:
            reset_after = int(data[0] + self.window_seconds - now) + 1
            return False, 0, max(1, reset_after)

        # Add current request
        data.append(now)
        cache.set(key, data, timeout=self.window_seconds)

        remaining = self.max_requests - len(data)
        reset_after = self.window_seconds

        return True, remaining, reset_after

    def get_limit_headers(self, allowed: bool, remaining: int, reset_after: int) -> Dict[str, str]:
        """Generate rate limit response headers."""
        return {
            'X-RateLimit-Limit': str(self.max_requests),
            'X-RateLimit-Remaining': str(remaining),
            'X-RateLimit-Reset': str(int(time.time() + reset_after)),
        }


class RateLimitMiddleware:
    """
    Middleware to apply rate limiting to all requests.
    Different limits for authenticated vs anonymous users.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.anonymous_limiter = RateLimiter(max_requests=60, window_seconds=60)
        self.authenticated_limiter = RateLimiter(max_requests=300, window_seconds=60)

    def __call__(self, request):
        # Skip rate limiting for health checks and static files
        if request.path.startswith('/health/') or request.path.startswith('/static/'):
            return self.get_response(request)

        # Generate identifier
        if request.user.is_authenticated:
            identifier = f"auth:{request.user.id}"
            limiter = self.authenticated_limiter
        else:
            identifier = f"ip:{self._get_client_ip(request)}"
            limiter = self.anonymous_limiter

        allowed, remaining, reset_after = limiter.is_allowed(identifier)

        if not allowed:
            logger.warning(f"Rate limit exceeded for {identifier}")

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                response = JsonResponse({
                    'error': 'Rate limit exceeded',
                    'retry_after': reset_after
                }, status=429)
            else:
                response = HttpResponseTooManyRequests(
                    content='Rate limit exceeded. Please try again later.'
                )

            response['Retry-After'] = str(reset_after)
            for header, value in limiter.get_limit_headers(allowed, remaining, reset_after).items():
                response[header] = value
            return response

        response = self.get_response(request)

        # Add rate limit headers
        for header, value in limiter.get_limit_headers(allowed, remaining, reset_after).items():
            response[header] = value

        return response

    def _get_client_ip(self, request) -> str:
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')


def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """
    Decorator for function-based rate limiting.
    Usage: @rate_limit(max_requests=10, window_seconds=60)
    """
    limiter = RateLimiter(max_requests=max_requests, window_seconds=window_seconds)

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            identifier = f"decorator:{request.user.id if request.user.is_authenticated else request.META.get('REMOTE_ADDR', 'unknown')}:{view_func.__name__}"

            allowed, remaining, reset_after = limiter.is_allowed(identifier)

            if not allowed:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': 'Rate limit exceeded',
                        'retry_after': reset_after
                    }, status=429)
                return HttpResponse('Rate limit exceeded.', status=429)

            response = view_func(request, *args, **kwargs)

            # Add headers
            for header, value in limiter.get_limit_headers(allowed, remaining, reset_after).items():
                response[header] = value

            return response
        return _wrapped_view
    return decorator