from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from apps.reports.models import GeneratedReport
from .models import SharedLink


@login_required
def create_share(request, report_id):
    report = get_object_or_404(GeneratedReport, id=report_id, query__user=request.user)
    
    is_public = request.POST.get('is_public', 'false') == 'true'
    expires_days = request.POST.get('expires_days', '')
    
    expires_at = None
    if expires_days:
        try:
            expires_at = timezone.now() + timedelta(days=int(expires_days))
        except ValueError:
            pass
    
    link = SharedLink.objects.create(
        report=report,
        token=SharedLink.generate_token(),
        is_public=is_public,
        expires_at=expires_at
    )
    
    messages.success(request, 'Share link created!')
    return redirect('collaboration:share_manage')


@login_required
def share_manage(request):
    links = SharedLink.objects.filter(
        report__query__user=request.user
    ).select_related('report', 'report__query').order_by('-created_at')
    
    return render(request, 'pages/collaboration/manage.html', {
        'links': links
    })


def share_access(request, token):
    link = get_object_or_404(SharedLink, token=token)
    
    if link.is_expired():
        raise Http404("This link has expired.")
    
    if not link.is_public and not request.user.is_authenticated:
        return redirect('accounts:login')
    
    link.increment_view()
    
    return render(request, 'pages/collaboration/view.html', {
        'link': link,
        'report': link.report
    })


@login_required
@require_http_methods(['POST'])
def revoke_share(request, pk):
    link = get_object_or_404(SharedLink, pk=pk, report__query__user=request.user)
    link.delete()
    messages.success(request, 'Share link revoked.')
    return redirect('collaboration:share_manage')