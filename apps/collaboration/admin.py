from django.contrib import admin
from .models import SharedLink


@admin.register(SharedLink)
class SharedLinkAdmin(admin.ModelAdmin):
    list_display = ('report', 'token', 'is_public', 'view_count', 'expires_at', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('token', 'report__query__query_text')
    readonly_fields = ('token', 'created_at')