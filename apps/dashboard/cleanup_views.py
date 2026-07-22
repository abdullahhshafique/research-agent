"""
Admin cleanup views.
"""
import logging
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.management import call_command
from django.http import JsonResponse
from apps.utils.search_cache import SearchCache

logger = logging.getLogger(__name__)


@staff_member_required
def cleanup_view(request):
    """Admin cleanup interface."""
    if request.method == 'POST':
        dry_run = request.POST.get('dry_run') == 'on'
        pdf_days = int(request.POST.get('pdf_days', 30))
        cache_days = int(request.POST.get('cache_days', 7))
        failed_days = int(request.POST.get('failed_days', 7))
        
        try:
            from io import StringIO
            out = StringIO()
            
            call_command(
                'cleanup',
                dry_run=dry_run,
                pdf_days=pdf_days,
                cache_days=cache_days,
                failed_days=failed_days,
                stdout=out
            )
            
            output = out.getvalue()
            
            if dry_run:
                messages.info(request, "Dry run completed. Check output below.")
            else:
                messages.success(request, "Cleanup completed successfully!")
            
            return render(request, 'pages/dashboard/cleanup.html', {
                'output': output,
                'dry_run': dry_run,
                'pdf_days': pdf_days,
                'cache_days': cache_days,
                'failed_days': failed_days,
            })
            
        except Exception as e:
            messages.error(request, f"Cleanup failed: {str(e)}")
            logger.error(f"Cleanup error: {e}")
    
    # Get cache stats
    cache = SearchCache()
    cache_stats = cache.get_stats()
    
    return render(request, 'pages/dashboard/cleanup.html', {
        'cache_stats': cache_stats,
        'pdf_days': 30,
        'cache_days': 7,
        'failed_days': 7,
    })


@staff_member_required
def cache_stats_api(request):
    """API endpoint for cache statistics."""
    cache = SearchCache()
    return JsonResponse(cache.get_stats())