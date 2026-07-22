from django.db import models
from django.conf import settings


class ResearchTemplate(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='templates'
    )
    name = models.CharField(max_length=100)
    query_pattern = models.TextField()
    description = models.TextField(blank=True)
    variables = models.JSONField(default=list, blank=True)
    is_public = models.BooleanField(default=False)
    usage_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'research_template'
        ordering = ['-usage_count', '-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_public']),
        ]
    
    def __str__(self):
        return self.name
    
    def increment_usage(self):
        self.usage_count += 1
        self.save(update_fields=['usage_count'])
    
    def render_query(self, **kwargs):
        query = self.query_pattern
        for key, value in kwargs.items():
            query = query.replace(f'{{{key}}}', str(value))
        return query