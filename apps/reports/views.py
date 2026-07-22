"""
Reports app views.
"""
import os
import logging
from django.shortcuts import render, get_object_or_404
from django.http import FileResponse, Http404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from apps.research.models import ResearchQuery
from .services.report_builder import ReportBuilder
from .services.pdf_engine import PDFExporter

logger = logging.getLogger(__name__)


@login_required
def report_preview(request, pk):
    """Preview report in HTML/Markdown."""
    research = get_object_or_404(ResearchQuery, pk=pk, user=request.user)
    
    if research.status != 'completed':
        raise Http404("Report not ready")
    
    report_md = ReportBuilder.from_research_query(research)
    
    return render(request, 'pages/reports/preview.html', {
        'research': research,
        'report': report_md
    })


@login_required
def report_download(request, pk):
    """Download report as PDF with logo support."""
    research = get_object_or_404(ResearchQuery, pk=pk, user=request.user)
    
    if research.status != 'completed':
        raise Http404("Report not ready")
    
    report_md = ReportBuilder.from_research_query(research)
    
    filename = f"research_{research.id}_{research.query_text[:30]}.pdf"
    output_path = os.path.join(settings.MEDIA_ROOT, 'reports', filename)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Get user's logo if available
    logo_url = None
    if hasattr(request.user, 'profile') and request.user.profile.logo_url:
        logo_url = request.user.profile.logo_url
    
    exporter = PDFExporter()
    exporter.export(
        markdown_content=report_md,
        title=f"Research: {research.query_text[:50]}",
        query=research.query_text,
        accent_color=request.user.profile.accent_color if hasattr(request.user, 'profile') else "#3B82F6",
        logo_url=logo_url,
        output_path=output_path
    )
    
    response = FileResponse(
        open(output_path, 'rb'),
        content_type='application/pdf'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response