from django.db import models
from django.conf import settings
from apps.research.models import ResearchQuery


class HistoryEntry(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='history_entries'
    )
    query = models.ForeignKey(
        ResearchQuery,
        on_delete=models.CASCADE,
        related_name='history_entry'
    )
    is_favorite = models.BooleanField(default=False)
    tags = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'history_entry'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['user', 'is_favorite']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.query.query_text[:30]}..."
    
    def toggle_favorite(self):
        self.is_favorite = not self.is_favorite
        self.save(update_fields=['is_favorite'])


class SearchHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='search_history'
    )
    search_term = models.CharField(max_length=200)
    result_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'search_history'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.search_term}"