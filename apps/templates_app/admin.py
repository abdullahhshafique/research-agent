from django.contrib import admin
from .models import ResearchTemplate


@admin.register(ResearchTemplate)
class ResearchTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_public', 'usage_count', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('name', 'query_pattern', 'user__username')