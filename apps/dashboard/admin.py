"""
Dashboard app admin.
"""
from django.contrib import admin
from .models import ApiKeyStore


@admin.register(ApiKeyStore)
class ApiKeyStoreAdmin(admin.ModelAdmin):
    list_display = ('key_name', 'is_active', 'rotated_at', 'rotated_by')
    list_filter = ('is_active', 'key_name')
    readonly_fields = ('created_at', 'rotated_at')
    search_fields = ('key_name',)

    def has_delete_permission(self, request, obj=None):
        """Prevent accidental deletion of API keys."""
        return request.user.is_superuser