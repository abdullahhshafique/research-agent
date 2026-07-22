"""
Research app admin.
"""
from django.contrib import admin
from .models import ResearchQuery, Source


class SourceInline(admin.TabularInline):
    model = Source
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(ResearchQuery)
class ResearchQueryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'query_text', 'status', 'version', 'is_latest', 'llm_model', 'created_at')
    list_filter = ('status', 'search_depth', 'llm_model', 'is_latest', 'created_at')
    search_fields = ('query_text', 'user__username')
    readonly_fields = ('created_at', 'started_at', 'completed_at', 'version')
    inlines = [SourceInline]


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('query', 'title', 'domain', 'relevance_score', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'url', 'domain')