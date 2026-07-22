import secrets
from datetime import timedelta
from django.db import models
from django.utils import timezone
from apps.reports.models import GeneratedReport


class SharedLink(models.Model):
    report = models.ForeignKey(
        GeneratedReport,
        on_delete=models.CASCADE,
        related_name='shared_links'
    )
    token = models.CharField(max_length=64, unique=True)
    is_public = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'shared_link'
        indexes = [
            models.Index(fields=['token']),
        ]
    
    def __str__(self):
        return f"Share for {self.report.query.query_text[:30]}..."
    
    @classmethod
    def generate_token(cls):
        return secrets.token_urlsafe(32)
    
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def increment_view(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def get_share_url(self):
        from django.urls import reverse
        return reverse('collaboration:share_access', kwargs={'token': self.token})