"""
Research app models.
"""
from django.db import models
from django.db.models import Q
from django.conf import settings


class ResearchQuery(models.Model):
    """
    Stores research queries and their results.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    SEARCH_DEPTH_CHOICES = [
        ('basic', 'Basic'),
        ('advanced', 'Advanced'),
    ]
    
    LLM_CHOICES = [
        ('groq', 'Groq (Llama 3.3)'),
        ('gemini', 'Google Gemini'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='research_queries'
    )
    query_text = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    search_depth = models.CharField(
        max_length=10,
        choices=SEARCH_DEPTH_CHOICES,
        default='advanced'
    )
    max_results = models.IntegerField(default=5)
    llm_model = models.CharField(
        max_length=20,
        choices=LLM_CHOICES,
        default='groq'
    )
    summary = models.TextField(blank=True, null=True)
    final_insight = models.TextField(blank=True, null=True)
    raw_sources = models.JSONField(blank=True, null=True)
    processing_time_ms = models.IntegerField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    
    # Versioning
    version = models.IntegerField(default=1)
    parent_query = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='versions'
    )
    is_latest = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'research_query'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['parent_query', 'is_latest']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.query_text[:50]}..."
    
    def create_new_version(self):
        """Create a new version of this query."""
        # Mark current as not latest
        self.is_latest = False
        self.save(update_fields=['is_latest'])
        
        # Create new version
        new_version = ResearchQuery.objects.create(
            user=self.user,
            query_text=self.query_text,
            search_depth=self.search_depth,
            max_results=self.max_results,
            llm_model=self.llm_model,
            parent_query=self.parent_query or self,
            version=self.version + 1 if self.parent_query else 2,
            is_latest=True
        )
        
        return new_version
    
    def get_version_history(self):
        """Get all versions of this query."""
        root = self.parent_query or self
        return ResearchQuery.objects.filter(
            Q(id=root.id) | Q(parent_query=root)
        ).order_by('version')
    
    def get_latest_version(self):
        """Get the latest version of this query."""
        root = self.parent_query or self
        try:
            return ResearchQuery.objects.get(parent_query=root, is_latest=True)
        except ResearchQuery.DoesNotExist:
            return root if root.is_latest else None


class Source(models.Model):
    """
    Individual search result source.
    """
    query = models.ForeignKey(
        ResearchQuery,
        on_delete=models.CASCADE,
        related_name='sources'
    )
    url = models.URLField(max_length=2000)
    title = models.CharField(max_length=500, blank=True)
    content = models.TextField(blank=True)
    relevance_score = models.FloatField(null=True, blank=True)
    domain = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'research_source'
        ordering = ['-relevance_score']
        indexes = [
            models.Index(fields=['query']),
        ]
    
    def __str__(self):
        return f"{self.title[:50]}... ({self.domain})"