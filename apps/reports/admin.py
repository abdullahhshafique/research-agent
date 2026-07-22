"""
Reports app admin.
"""
from django.contrib import admin
from .models import GeneratedReport


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ('query', 'file_size_bytes', 'download_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('query__query_text',)
    readonly_fields = ('created_at',)