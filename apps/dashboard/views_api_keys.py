"""
API Key management views.
"""
import logging
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings

from .models import ApiKeyStore

logger = logging.getLogger(__name__)


@staff_member_required
def api_keys(request):
    """API key status and management page."""
    # Ensure keys are synced from env
    ApiKeyStore.sync_from_env()

    keys = ApiKeyStore.objects.all().order_by('key_name')

    # Also show raw env status
    env_status = {
        'GROQ_API_KEY': bool(settings.GROQ_API_KEY),
        'TAVILY_API_KEY': bool(settings.TAVILY_API_KEY),
        'GOOGLE_API_KEY': bool(settings.GOOGLE_API_KEY),
    }

    return render(request, 'pages/dashboard/keys.html', {
        'keys': keys,
        'env_status': env_status,
    })


@staff_member_required
@require_POST
def rotate_api_key(request):
    """Rotate an API key at runtime."""
    key_name = request.POST.get('key_name', '').strip().lower()
    new_value = request.POST.get('new_value', '').strip()

    if not key_name or not new_value:
        messages.error(request, 'Key name and new value are required.')
        return redirect('dashboard:api_keys')

    if key_name not in ['groq', 'tavily', 'google']:
        messages.error(request, 'Invalid key name.')
        return redirect('dashboard:api_keys')

    try:
        key_store, created = ApiKeyStore.objects.get_or_create(
            key_name=key_name,
            defaults={'key_value': new_value}
        )

        if not created:
            key_store.rotate(new_value, user=request.user)

        # Update settings in-memory for current process
        setting_name = f"{key_name.upper()}_API_KEY"
        setattr(settings, setting_name, new_value)

        # Mask value for display
        masked = new_value[:8] + '...' + new_value[-4:] if len(new_value) > 12 else '****'
        messages.success(request, f'{key_name.upper()} API key rotated successfully. New key: {masked}')
        logger.info(f"API key {key_name} rotated by {request.user.username}")

    except Exception as e:
        messages.error(request, f'Failed to rotate key: {str(e)}')
        logger.error(f"API key rotation failed: {e}")

    return redirect('dashboard:api_keys')


@staff_member_required
@require_POST
def deactivate_api_key(request):
    """Deactivate an API key."""
    key_name = request.POST.get('key_name', '').strip().lower()

    try:
        key_store = ApiKeyStore.objects.get(key_name=key_name)
        key_store.deactivate()

        # Update settings in-memory
        setting_name = f"{key_name.upper()}_API_KEY"
        setattr(settings, setting_name, '')

        messages.success(request, f'{key_name.upper()} API key deactivated.')
        logger.info(f"API key {key_name} deactivated by {request.user.username}")

    except ApiKeyStore.DoesNotExist:
        messages.error(request, 'Key not found.')

    return redirect('dashboard:api_keys')


@staff_member_required
def api_key_status_api(request):
    """AJAX endpoint for API key status."""
    ApiKeyStore.sync_from_env()
    keys = ApiKeyStore.objects.all()

    return JsonResponse({
        'keys': [
            {
                'name': k.key_name,
                'active': k.is_active,
                'rotated_at': k.rotated_at.isoformat() if k.rotated_at else None,
                'has_value': bool(k.key_value),
            }
            for k in keys
        ]
    })