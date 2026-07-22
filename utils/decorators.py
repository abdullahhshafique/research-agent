"""
Custom decorators.
"""
from functools import wraps
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied


def require_ajax(view_func):
    """
    Decorator to require AJAX requests.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'AJAX required'}, status=400)
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def require_premium(view_func):
    """
    Decorator to require premium user (or admin).
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            raise PermissionDenied("Premium subscription required.")
        role = request.user.profile.role
        if role not in ('premium', 'admin'):
            raise PermissionDenied("Premium subscription required.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view