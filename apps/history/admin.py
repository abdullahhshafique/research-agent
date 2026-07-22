from django.contrib import admin
from .models import HistoryEntry, SearchHistory


@admin.register(HistoryEntry)
class HistoryEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'query', 'is_favorite', 'created_at')
    list_filter = ('is_favorite', 'created_at')
    search_fields = ('query__query_text', 'user__username')
    readonly_fields = ('created_at',)


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'search_term', 'result_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('search_term', 'user__username')