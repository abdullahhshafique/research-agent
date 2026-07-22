from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from apps.research.models import ResearchQuery
from .models import HistoryEntry, SearchHistory
from django.views.decorators.http import require_POST

@login_required
def history_list(request):
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('q', '')
    show_favorites = request.GET.get('favorites', '') == '1'
    
    queryset = ResearchQuery.objects.filter(user=request.user)
    
    if status_filter != 'all':
        queryset = queryset.filter(status=status_filter)
    
    if show_favorites:
        favorite_ids = HistoryEntry.objects.filter(
            user=request.user, 
            is_favorite=True
        ).values_list('query_id', flat=True)
        queryset = queryset.filter(id__in=favorite_ids)
    
    if search_query:
        queryset = queryset.filter(
            Q(query_text__icontains=search_query) |
            Q(summary__icontains=search_query)
        )
        SearchHistory.objects.create(
            user=request.user,
            search_term=search_query,
            result_count=queryset.count()
        )
    
    queryset = queryset.order_by('-created_at')
    
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get favorite status
    favorite_ids = set(HistoryEntry.objects.filter(
        user=request.user,
        is_favorite=True
    ).values_list('query_id', flat=True))
    
    for item in page_obj:
        item.is_fav = item.id in favorite_ids
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'show_favorites': show_favorites,
        'total_count': paginator.count,
    }
    
    return render(request, 'pages/history/list.html', context)


@login_required
@require_http_methods(['POST'])
def toggle_favorite(request, pk):
    query = get_object_or_404(ResearchQuery, pk=pk, user=request.user)
    
    entry, created = HistoryEntry.objects.get_or_create(
        user=request.user,
        query=query,
        defaults={'is_favorite': True}
    )
    
    if not created:
        entry.toggle_favorite()
    
    return JsonResponse({
        'status': 'success',
        'is_favorite': entry.is_favorite
    })

@login_required
@require_POST
def bulk_delete_history(request):
    """Delete multiple history items at once."""
    import json
    data = json.loads(request.body)
    ids = data.get('ids', [])
    
    if not ids:
        return JsonResponse({"status": "error", "message": "No items selected"})
    
    # Verify ownership
    deleted = ResearchQuery.objects.filter(
        id__in=ids,
        user=request.user
    ).delete()
    
    return JsonResponse({
        "status": "success",
        "deleted": deleted[0],
        "message": f"Deleted {deleted[0]} items"
    })


@login_required
@require_http_methods(['POST'])
def delete_history(request, pk):
    query = get_object_or_404(ResearchQuery, pk=pk, user=request.user)
    query.delete()
    messages.success(request, 'Research entry deleted.')
    return redirect('history:history_list')

@login_required
@require_POST
def save_as_template(request, pk):
    """Save a research query as a template."""
    query = get_object_or_404(ResearchQuery, pk=pk, user=request.user)

    name = request.POST.get('name', '').strip()
    if not name:
        return JsonResponse({"status": "error", "message": "Template name is required"})

    from apps.templates_app.models import ResearchTemplate

    template = ResearchTemplate.objects.create(
        user=request.user,
        name=name,
        query_pattern=query.query_text,
        description=f"Created from research query (ID: {query.id})",
        is_public=False
    )

    return JsonResponse({
        "status": "success",
        "template_id": template.id,
        "message": f"Template '{name}' created successfully!"
    })